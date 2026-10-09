import re
import threading
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw


class LocalImageGenerator:
    def __init__(self, model_id: str, mock: bool = False):
        self.model_id = model_id
        self.mock = mock
        self._pipeline = None
        self._load_lock = threading.Lock()

    def _load(self):
        if self._pipeline is not None:
            return self._pipeline
        with self._load_lock:
            if self._pipeline is not None:
                return self._pipeline
            import torch
            from diffusers import (
                AutoPipelineForImage2Image,
                DiffusionPipeline,
                DPMSolverMultistepScheduler,
            )

            load_options = {"torch_dtype": torch.float16, "use_safetensors": True}
            if "xl" in self.model_id.lower():
                load_options["variant"] = "fp16"
            pipe = DiffusionPipeline.from_pretrained(self.model_id, **load_options)
            pipeline = AutoPipelineForImage2Image.from_pipe(pipe)
            pipeline.enable_attention_slicing()
            if hasattr(pipeline, "enable_vae_slicing"):
                pipeline.enable_vae_slicing()
            elif hasattr(pipeline.vae, "enable_slicing"):
                pipeline.vae.enable_slicing()
            if torch.cuda.is_available() and "xl" not in self.model_id.lower():
                pipeline.to("cuda")
            else:
                pipeline.enable_model_cpu_offload()
            pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                pipeline.scheduler.config,
                algorithm_type="dpmsolver++",
                use_karras_sigmas=True,
            )
            self._pipeline = pipeline
            return self._pipeline

    def preload(self) -> None:
        """Load model weights before the user presses the generation button."""
        if not self.mock:
            self._load()

    def generate(
        self,
        prompt: str,
        seed: int,
        width: int = 768,
        height: int = 1024,
        steps: int = 30,
        guidance: float = 7.0,
    ) -> bytes:
        if self.mock:
            image = Image.new("RGB", (width, height), "#e9eef5")
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
            if "crocs-style" in prompt.lower() or "clogs" in prompt.lower():
                negatives.extend(["sneakers", "sandals", "slides", "open-toe shoes"])
            if ("trousers" in prompt or "long pants" in prompt) and "shorts" not in prompt:
                negatives.extend(["shorts", "cropped pants", "bare legs"])
            if "glasses:" not in prompt.lower():
                negatives.extend(["glasses", "sunglasses"])
            pose_path = self._pose_path(prompt)
            pose_image = Image.open(pose_path).convert("RGB").resize(
                (width, height), Image.Resampling.LANCZOS
            )
            exact_reference = "glasses:" in prompt.lower() and (
                "crocs-style" in prompt.lower() or "clogs" in prompt.lower()
            )
            image = pipe(
                prompt=prompt,
                negative_prompt=", ".join(negatives),
                image=pose_image,
                # Preserve the clean reference face, glasses, shoes and neutral
                # proportions while still allowing requested clothing changes.
                strength=0.32 if exact_reference else (0.76 if steps >= 30 else 0.72),
                num_inference_steps=steps,
                guidance_scale=guidance,
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
        if female:
            return assets / "neutral-front-female.png"
        if "glasses:" in normalized:
            return assets / "product-style-male-glasses-crocs.png"
        return assets / "product-style-male-no-glasses.png"

    def release_gpu_cache(self) -> None:
        if self.mock:
            return
        import gc

        import torch

        self._pipeline = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

