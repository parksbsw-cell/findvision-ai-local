from .schemas import Appearance

TRANSLATIONS = {
    "고무신": "traditional Korean rubber shoes",
    "지팡이": "walking cane",
    "반팔티": "short-sleeve T-shirt",
    "긴팔티": "long-sleeve T-shirt",
    "반바지": "shorts",
    "긴바지": "long pants",
    "자켓": "jacket",
    "재킷": "jacket",
    "우산": "umbrella",
    "가방": "bag",
}


def translate_terms(value: str) -> str:
    result = value
    for source, target in TRANSLATIONS.items():
        result = result.replace(source, target)
    return result


def visual_requirements(a: Appearance) -> list[str]:
    values = [
        a.gender, f"{a.age} years old" if a.age else "", a.body_type, a.hair,
        a.top, a.outerwear, a.bottom, a.shoes, a.hat, a.glasses, a.facial_hair,
        *a.accessories,
    ]
    return [translate_terms(value) for value in values if value]


def image_prompt(a: Appearance, correction: str = "") -> str:
    requirements = visual_requirements(a)
    prompt = (
        "Documentary full-body reference photograph of one person standing naturally, "
        "plain light-gray studio background, Korean public safety reference style, neutral pose, "
        "realistic anatomy, both hands and both feet fully visible. The person's face is generic "
        "and must not resemble a real named person. Explicit appearance: "
        + "; ".join(requirements)
        + ". Do not add unstated clothing, accessories, logos, text, watermark, or props."
    )
    if correction:
        prompt += " Correct the previous image: " + correction
    return prompt


def verification_prompt(a: Appearance) -> str:
    return (
        "You are checking an AI-generated missing-person appearance reference image. "
        "Compare only the explicit requirements below. Do not infer identity. Return strict JSON "
        "with passed(boolean), score(0-100), missing(array), wrong(array), feedback(string). "
        "Requirements: " + "; ".join(visual_requirements(a))
    )

