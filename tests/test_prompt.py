from app.prompt import image_prompt, visual_requirements
from app.schemas import Appearance


def test_prompt_keeps_rubber_shoes_and_cane():
    appearance = Appearance(
        shoes="검은색 고무신",
        accessories=["오른손에 갈색 지팡이"],
    )
    requirements = visual_requirements(appearance)
    assert any("traditional Korean rubber shoes" in item for item in requirements)
    assert any("walking cane" in item for item in requirements)
    prompt = image_prompt(appearance)
    assert "Do not add unstated" in prompt

