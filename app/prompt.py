from .schemas import Appearance

TRANSLATIONS = {
    "겉 셔츠 모든 단추를 풀어 입음": "outer shirt fully unbuttoned and open",
    "오른손에": "in right hand",
    "왼손에": "in left hand",
    "양손에": "in both hands",
    "보행용": "walking",
    "검은색": "solid black",
    "검정색": "solid black",
    "흰색": "white",
    "하얀색": "white",
    "회색": "gray",
    "갈색": "brown",
    "남색": "navy",
    "파란색": "blue",
    "빨간색": "red",
    "초록색": "green",
    "노란색": "yellow",
    "분홍색": "pink",
    "보라색": "purple",
    "베이지색": "beige",
    "남성": "Korean man",
    "남자": "Korean man",
    "남": "Korean man",
    "여성": "Korean woman",
    "여자": "Korean woman",
    "여": "Korean woman",
    "마른 편": "slim build",
    "통통한 편": "stocky build",
    "보통 체형": "average build",
    "고도 비만": "very heavy build",
    "비만": "heavy build",
    "저체중": "underweight build",
    "얇은": "thin",
    " 위에 ": " over ",
    "짧은 머리": "short hair",
    "긴 머리": "long hair",
    "머리카락": "hair",
    "머리": "hair",
    "학교": "school",
    "반팔 셔츠": "short-sleeve button-up shirt",
    "긴팔 셔츠": "long-sleeve button-up shirt",
    "크록스": "closed-toe Crocs-style foam clogs with ventilation holes and heel straps",
    "안경": "clearly visible eyeglasses",
    "고무신": "Korean rubber slip-on shoes",
    "지팡이": "walking cane",
    "반팔티": "short-sleeve T-shirt",
    "긴팔티": "long-sleeve T-shirt",
    "반팔": "short-sleeve T-shirt",
    "긴팔": "long-sleeve T-shirt",
    "반바지": "shorts",
    "긴바지": "long pants",
    "바지": "full-length trousers",
    "상의": "top",
    "하의": "bottom",
    "신발": "shoes",
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
        a.gender, f"{a.age} years old" if a.age else "",
        f"{a.height} cm tall" if a.height else "",
        f"{a.weight} kg" if a.weight else "",
        a.body_type, a.hair,
        a.top, a.outerwear, a.bottom, a.shoes, a.hat, a.glasses, a.facial_hair,
        *a.accessories,
    ]
    return [translate_terms(value) for value in values if value]


def subject_description(a: Appearance) -> str:
    gender = translate_terms(a.gender) if a.gender else "Korean person"
    if not a.age:
        return gender
    try:
        age = int(a.age)
    except ValueError:
        return f"{a.age}-year-old {gender}"
    if age <= 12:
        role = "Korean boy" if "man" in gender else "Korean girl" if "woman" in gender else "Korean child"
    elif age <= 19:
        role = "Korean teenage boy" if "man" in gender else "Korean teenage girl" if "woman" in gender else "Korean teenager"
    elif age >= 65:
        role = "elderly Korean man" if "man" in gender else "elderly Korean woman" if "woman" in gender else "elderly Korean person"
    else:
        role = gender
    return f"{age}-year-old {role}"


def image_prompt(a: Appearance, correction: str = "") -> str:
    requirements = visual_requirements(a)
    subject = subject_description(a)
    clothing = [
        translate_terms(value)
        for value in (a.top, a.outerwear, a.bottom, a.shoes, a.hat, a.glasses)
        if value
    ]
    prompt = (
        "SUBJECT: exactly one " + subject + ". The subject must visibly match this Korean age group. "
        "MANDATORY VISIBLE CLOTHING: " + "; ".join(clothing) + ". "
        "Documentary studio photograph of EXACTLY ONE person. The same person must appear only once. "
        "Standing straight, front-facing, arms relaxed at the sides, centered, neutral expression. "
        "Single uninterrupted head-to-toe view, hands and feet visible. "
        "The clothing colors and garment types below are mandatory and must be literal. Required: "
        + "; ".join(requirements)
        + ". Plain light gray background. Photorealistic Korean missing-person appearance reference. "
        "No collage, no inset, no alternate pose, no second person, no props unless explicitly required. "
        "Repeat exactly: " + "; ".join(clothing) + "."
    )
    if correction:
        prompt += " Correct the previous image: " + correction
    return prompt


def verification_prompt(a: Appearance) -> str:
    return (
        "You are checking an AI-generated missing-person appearance reference image. "
        "Compare only the explicit requirements below. Do not infer identity. No reasoning. Return JSON "
        "with passed(boolean), score(0-100), missing(array), wrong(array), feedback(string). "
        "Mark any extra visible accessory as wrong. Requirements: "
        + "; ".join(visual_requirements(a))
    )

