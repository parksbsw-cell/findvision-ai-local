from app.providers.diffusers_local import LocalImageGenerator


def test_mock_generator_honors_fast_and_detailed_dimensions():
    generator = LocalImageGenerator("unused", mock=True)

    fast = generator.generate("test", 1, width=512, height=768, steps=20)
    detailed = generator.generate("test", 1, width=896, height=1152, steps=30)

    from io import BytesIO

    from PIL import Image

    assert Image.open(BytesIO(fast)).size == (512, 768)
    assert Image.open(BytesIO(detailed)).size == (896, 1152)
