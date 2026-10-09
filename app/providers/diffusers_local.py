from io import BytesIO

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
        from diffusers import DiffusionPipeline

        pipe = DiffusionPipeline.from_pretrained(
            self.model_id,
            variant="fp16",
            torch_dtype=torch.float16,
            use_safetensors=True,
        )
        pipe.enable_model_cpu_offload()
        pipe.enable_attention_slicing()
        self._pipeline = pipe
        return pipe

    def generate(self, prompt: str, seed: int) -> bytes:
        if self.mock:
            image = Image.new("RGB", (512, 768), "#e9eef5")
            draw = ImageDraw.Draw(image)
            draw.text((24, 24), f"FindVision local test\nseed={seed}", fill="#172033")
        else:
            import torch

            pipe = self._load()
            generator = torch.Generator(device="cpu").manual_seed(seed)
            negatives = [
                "hands in pockets", "hidden hands", "crossed arms", "folded arms", "bent arms", "fashion pose",
                "belt", "vignette", "dramatic lighting",
                "cropped body", "missing feet", "two people", "anime", "illustration",
            ]
            if "solid black short sleeve" in prompt:
                negatives.extend(["white shirt", "gray shirt", "colored shirt"])
            if "short sleeve" in prompt and "outer" not in prompt:
                negatives.extend(["long sleeves", "jacket", "coat"])
            if "Crocs clogs" in prompt:
                negatives.extend(["sneakers", "sandals", "slides", "open-toe shoes"])
            if ("trousers" in prompt or "long pants" in prompt) and "shorts" not in prompt:
                negatives.extend(["shorts", "cropped pants", "bare legs"])
            image = pipe(
                prompt=prompt,
                negative_prompt=", ".join(negatives),
                width=768,
                height=1024,
                num_inference_steps=28,
                guidance_scale=8.0,
                generator=generator,
            ).images[0]
        output = BytesIO()
        image.save(output, format="PNG", optimize=True)
        return output.getvalue()

    def release_gpu_cache(self) -> None:
        if self.mock:
            return
        import gc

        import torch

        self._pipeline = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

