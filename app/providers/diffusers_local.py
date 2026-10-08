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
                "cropped body", "missing feet", "extra fingers", "duplicate person", "two people",
                "multiple people", "second person", "repeated person", "alternate pose", "text",
                "watermark", "logo", "inaccurate clothing", "extra accessories",
                "collage", "split screen", "multiple views", "inset image", "contact sheet",
            ]
            if "short-sleeve" in prompt and "outer" not in prompt:
                negatives.extend(["long sleeves", "jacket", "coat", "outerwear"])
            if "Crocs-style" in prompt:
                negatives.extend(["sneakers", "lace-up shoes", "sandals", "slides", "flip-flops"])
            if "trousers" in prompt and "shorts" not in prompt:
                negatives.extend(["shorts", "bare legs"])
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

