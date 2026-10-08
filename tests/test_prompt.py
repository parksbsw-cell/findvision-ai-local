from app.prompt import image_prompt, visual_requirements
from app.schemas import Appearance


def test_prompt_keeps_rubber_shoes_and_cane():
    appearance = Appearance(
        shoes="검은색 고무신",
        accessories=["오른손에 갈색 지팡이"],
    )
    requirements = visual_requirements(appearance)
    assert any("Korean rubber slip-on shoes" in item for item in requirements)
    assert any("walking cane" in item for item in requirements)
    prompt = image_prompt(appearance)
    assert "hands and feet visible" in prompt


def test_prompt_translates_critical_korean_terms_and_stays_compact():
    appearance = Appearance(
        gender="남성", age="17", body_type="마른 편",
        top="검은색 얇은 반팔티 위에 흰색 학교 반팔 셔츠 (겉 셔츠 모든 단추를 풀어 입음)",
        bottom="검은색 반바지", shoes="검은색 고무신",
        accessories=["오른손에 갈색 지팡이"],
    )
    prompt = image_prompt(appearance)
    assert "Korean man" in prompt
    assert "17-year-old Korean teenage boy" in prompt
    assert "outer shirt fully unbuttoned" in prompt
    assert "in right hand brown walking cane" in prompt
    assert not any("가" <= char <= "힣" for char in prompt)


def test_prompt_translates_compact_alert_terms():
    prompt = image_prompt(Appearance(gender="남", age="18", height="175", weight="74", top="검은색 반팔", bottom="검은색 바지", shoes="검은색 크록스", glasses="안경"))
    assert "Korean man" in prompt
    assert "175 cm tall" in prompt
    assert "short-sleeve T-shirt" in prompt
    assert "Crocs-style foam clogs" in prompt
    assert "full-length trousers" in prompt
    assert "eyeglasses" in prompt
    assert "EXACTLY ONE person" in prompt
    assert "18-year-old Korean teenage boy" in prompt
    assert not any("가" <= char <= "힣" for char in prompt)

