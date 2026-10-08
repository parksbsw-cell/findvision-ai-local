import re

from .schemas import Appearance

COLORS = r"검은색|검정색|흰색|하얀색|회색|갈색|남색|파란색|빨간색|초록색|노란색|분홍색|보라색|베이지색"
SHOES = r"고무신|크록스|운동화|슬리퍼|샌들|구두|단화|부츠|장화|신발"
TOPS = r"반팔[ ]*셔츠|긴팔[ ]*셔츠|반팔티|긴팔티|티셔츠|셔츠|남방|니트|맨투맨|후드티|조끼"
OUTER = r"자켓|재킷|점퍼|코트|패딩|바람막이|후드집업|외투|겉옷|작업복"
BOTTOMS = r"반바지|긴바지|청바지|면바지|슬랙스|치마|치마바지|바지"


def _first(pattern: str, text: str, group: int = 1) -> str:
    match = re.search(pattern, text)
    return match.group(group).strip() if match else ""


def _garment(text: str, kinds: str) -> str:
    return _first(
        rf"((?:{COLORS})?\s*(?:얇은\s*|두꺼운\s*)?(?:학교\s*)?(?:{kinds}))", text
    )


def _tops(text: str) -> str:
    pattern = rf"((?:{COLORS})?\s*(?:얇은\s*|두꺼운\s*)?(?:학교\s*)?(?:{TOPS}))"
    found = []
    for value in re.findall(pattern, text):
        value = re.sub(r"\s+", " ", value).strip()
        if value and value not in found:
            found.append(value)
    result = " 위에 ".join(found)
    if len(found) > 1 and re.search(r"모든\s*단추(?:를)?\s*풀|단추\s*전체\s*오픈", text):
        result += " (겉 셔츠 모든 단추를 풀어 입음)"
    return result


def is_missing_alert(text: str) -> bool:
    missing = bool(re.search(r"실종|찾습니다|배회|보호자를\s*찾", text))
    person = bool(re.search(r"\d{1,3}\s*세|남성|여성|남자|여자|키\s*\d", text))
    action = bool(re.search(r"착용|인상착의|발견\s*시|경찰서|경찰청", text))
    return missing and person and action


def parse_message(text: str) -> tuple[Appearance, list[str]]:
    normalized = re.sub(r"\s+", " ", text).strip()
    accessories: list[str] = []
    accessory_patterns = [
        rf"((?:왼손|오른손|양손)(?:에|으로)?\s*(?:{COLORS})?\s*(?:보행용\s*)?지팡이)",
        rf"((?:왼손|오른손|양손)(?:에|으로)?\s*(?:{COLORS})?\s*우산)",
        rf"((?:{COLORS})?\s*(?:백팩|손가방|가방|지갑|휴대폰|스마트폰|목걸이|팔찌|손목시계|시계|보청기))",
    ]
    for pattern in accessory_patterns:
        for value in re.findall(pattern, normalized):
            value = re.sub(r"\s+", " ", value).strip()
            if value and value not in accessories:
                accessories.append(value)

    hair_parts = []
    for pattern in (
        rf"((?:{COLORS})\s*(?:머리|머리카락))",
        r"(짧은\s*머리|긴\s*머리)",
        r"(장발|단발머리|단발|반삭머리|반삭|삭발|버섯머리|투블럭|숏컷|곱슬머리|곱슬|직모|생머리)",
    ):
        value = _first(pattern, normalized)
        if value and value not in hair_parts:
            hair_parts.append(value)

    body = _first(r"(고도\s*비만|비만|저체중|통통한\s*편|마른\s*편|건장한\s*편|보통\s*체형)", normalized)
    appearance = Appearance(
        gender=_first(r"(남성|여성|남자|여자)", normalized),
        age=_first(r"(\d{1,3})\s*세", normalized),
        height=_first(r"키\s*(\d{2,3})\s*cm", normalized),
        weight=_first(r"몸무게\s*(\d{2,3})\s*kg", normalized),
        body_type=body,
        hair=" ".join(hair_parts),
        top=_tops(normalized),
        outerwear=_garment(normalized, OUTER),
        bottom=_garment(normalized, BOTTOMS),
        shoes=_garment(normalized, SHOES),
        hat=_first(rf"((?:{COLORS})?\s*(?:캡모자|야구모자|등산모자|벙거지|버킷햇|비니|모자))", normalized),
        glasses="안경" if re.search(r"안경\s*(?:착용|씀|쓴)", normalized) else "",
        facial_hair=_first(r"(콧수염|턱수염|수염)", normalized),
        accessories=accessories,
        last_seen=_first(r"(?:마지막\s*)?목격(?:\s*위치|\s*장소)?\s*[:：]?\s*([^,.]+)", normalized),
    )
    warnings = []
    if not is_missing_alert(normalized):
        warnings.append("실종 재난문자 형식을 확정하지 못했습니다.")
    if not any((appearance.top, appearance.outerwear, appearance.bottom, appearance.shoes)):
        warnings.append("옷이나 신발 정보가 없어 이미지 정확도가 낮을 수 있습니다.")
    return appearance, warnings

