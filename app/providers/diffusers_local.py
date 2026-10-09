import re
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw


class LocalImageGenerator:
    def __init__(self, model_id: str, mock: bool = False):
        self.model_id = model_id
        self.mock = mock
        self._pipeline = None

    def _load(self):
        if self._pipeline is not None:
            return self._pipeline
        import torch
        from diffusers import AutoPipelineForImage2Image, DiffusionPipeline

        pipe = DiffusionPipeline.from_pretrained(
            self.model_id,
            variant="fp16",
            torch_dtype=torch.float16,
            use_safetensors=True,
        )
        pipe.enable_model_cpu_offload()
        pipe.enable_attention_slicing()
        self._pipeline = AutoPipelineForImage2Image.from_pipe(pipe)
        return self._pipeline

    def generate(self, prompt: str, seed: int) -> bytes:
        if self.mock:
            image = Image.new("RGB", (512, 768), "#e9eef5")
            draw = ImageDraw.Draw(image)
            draw.text((24, 24), f"FindVision local test\nseed={seed}", fill="#172033")
        else:
            import torch

            self._load()
            pipe = self._pipeline
            generator = torch.Generator(device="cpu").manual_seed(seed)
            negatives = [
                "hands in pockets", "crossed arms", "fashion pose", "fashion model",
                "makeup", "beauty retouching", "glamour", "smiling", "belt", "vignette",
                "dramatic lighting", "cropped body", "missing feet", "extra person",
                "extra limbs", "extra shoes", "anime", "illustration",
                "logo", "emblem", "badge", "brand mark", "letters", "text on clothes",
                "decorative patch", "school badge", "club badge", "two-tone outerwear",
                "multicolor jacket", "color-block jacket", "striped sleeves",
            ]
            # Color mistakes are especially harmful in a missing-person reference.
            # Exclude competing garment colors when the requested color is explicit.
            outerwear_color_negatives = {
                "red": ["navy jacket", "blue jacket", "black jacket", "white jacket", "gray jacket"],
                "black": ["red jacket", "navy jacket", "blue jacket", "white jacket", "gray jacket"],
                "white": ["red jacket", "navy jacket", "blue jacket", "black jacket", "gray jacket"],
                "navy": ["red jacket", "blue jacket", "black jacket", "white jacket", "gray jacket"],
                "gray": ["red jacket", "navy jacket", "blue jacket", "black jacket", "white jacket"],
            }
            outerwear_match = re.search(
                r"OUTERWEAR:\s*(?:solid\s+)?(red|black|white|navy|gray)\b",
                prompt,
                re.IGNORECASE,
            )
            if outerwear_match:
                negatives.extend(outerwear_color_negatives[outerwear_match.group(1).lower()])
            if "solid black short sleeve" in prompt:
                negatives.extend(["white shirt", "gray shirt", "colored shirt"])
            if "short sleeve" in prompt and "outer" not in prompt:
                negatives.extend(["long sleeves", "jacket", "coat"])
            if "Crocs clogs" in prompt:
                negatives.extend(["sneakers", "sandals", "slides", "open-toe shoes"])
            if ("trousers" in prompt or "long pants" in prompt) and "shorts" not in prompt:
                negatives.extend(["shorts", "cropped pants", "bare legs"])
            pose_path = self._pose_path(prompt)
            pose_image = Image.open(pose_path).convert("RGB").resize((768, 1024), Image.Resampling.LANCZOS)
            image = pipe(
                prompt=prompt,
                negative_prompt=", ".join(negatives),
                image=pose_image,
                strength=0.98,
                num_inference_steps=32,
                guidance_scale=7.5,
                generator=generator,
            ).images[0]
        output = BytesIO()
        image.save(output, format="PNG", optimize=True)
        return output.getvalue()

    @staticmethod
    def _pose_path(prompt: str) -> Path:
        normalized = prompt.lower()
        age_match = re.search(r"\bage\s*:\s*(\d{1,3})", normalized)
        age = int(age_match.group(1)) if age_match else None
        female = any(marker in normalized for marker in ("gender: female", " woman", " girl"))
        assets = Path(__file__).resolve().parents[1] / "assets"
        if age is not None and age <= 12:
            return assets / ("neutral-front-girl.png" if female else "neutral-front-boy.png")
        return assets / ("neutral-front-female.png" if female else "neutral-front-pose-v2.png")

    def release_gpu_cache(self) -> None:
        if self.mock:
            return
        import gc

        import torch

        self._pipeline = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

