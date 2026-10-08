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
            image = pipe(
                prompt=prompt,
                negative_prompt=(
                    "cropped body, missing feet, extra fingers, duplicate person, text, watermark, "
                    "logo, inaccurate clothing, extra accessories"
                ),
                width=768,
                height=1024,
                num_inference_steps=28,
                guidance_scale=6.5,
                generator=generator,
            ).images[0]
        output = BytesIO()
        image.save(output, format="PNG", optimize=True)
        return output.getvalue()

