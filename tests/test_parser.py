from app.parser import is_missing_alert, parse_message


def test_complex_korean_appearance_is_preserved():
    text = (
        "실종 남성 81세, 키 167cm, 마른 편, 검은색 반팔티, 회색 자켓, "
        "검은색 반바지, 검은색 고무신, 오른손에 갈색 보행용 지팡이. "
        "발견 시 경찰서로 연락 바랍니다."
    )
    facts, warnings = parse_message(text)
    assert is_missing_alert(text)
    assert warnings == []
    assert facts.top == "검은색 반팔티"
    assert facts.outerwear == "회색 자켓"
    assert facts.bottom == "검은색 반바지"
    assert facts.shoes == "검은색 고무신"
    assert facts.body_type == "마른 편"
    assert facts.accessories == ["오른손에 갈색 보행용 지팡이"]


def test_unstated_hair_and_accessories_are_not_invented():
    facts, _ = parse_message("실종 여성 70세, 흰색 고무신 착용, 발견 시 경찰서 연락")
    assert facts.hair == ""
    assert facts.accessories == []


def test_general_message_is_not_missing_alert():
    assert not is_missing_alert("오늘 비가 많이 오니 안전에 주의하세요.")


def test_layered_school_shirt_and_unbuttoned_state_are_preserved():
    facts, _ = parse_message(
        "실종 남성 17세, 안에 검은색 얇은 반팔티, 그 위에 흰색 학교 반팔 셔츠를 "
        "입고 모든 단추를 풀었으며 검은색 반바지 착용, 발견 시 경찰서 연락"
    )
    assert "검은색 얇은 반팔티" in facts.top
    assert "흰색 학교 반팔 셔츠" in facts.top
    assert "모든 단추를 풀어 입음" in facts.top


def test_compact_copied_profile_is_accepted():
    text = "이름 구자윤, 남,18세, 175CM,74KG, 검은색 반팔, 검은색 바지, 검은색 크록스, 안경"
    facts, warnings = parse_message(text)
    assert is_missing_alert(text)
    assert warnings == []
    assert facts.name == "구자윤"
    assert facts.gender == "남"
    assert facts.height == "175"
    assert facts.weight == "74"
    assert facts.top == "검은색 반팔"
    assert facts.bottom == "검은색 바지"
    assert facts.shoes == "검은색 크록스"
    assert facts.glasses == "안경"


def test_realistic_alert_headers_and_parentheses_are_accepted():
    text = (
        "[실종경보] 서울경찰청 실종자 김철수(남, 81세)를 찾습니다. "
        "167cm, 63kg, 회색 자켓, 갈색체크바지, 검정 고무신"
    )
    facts, _ = parse_message(text)
    assert is_missing_alert(text)
    assert facts.name == "김철수"
    assert facts.height == "167"
    assert facts.weight == "63"
    assert facts.outerwear == "회색 자켓"
    assert facts.bottom == "갈색체크바지"


def test_non_missing_weather_alert_stays_rejected():
    assert not is_missing_alert("[안전안내문자] 오늘 18시부터 강풍과 많은 비가 예상됩니다.")


def test_labeled_public_alert_fields_are_parsed():
    text = (
        "[실종자 발생] 성명: 김○○, 성별: 여, 76세, 신장: 153, 체중: 48, "
        "상의: 빨간색, 하의: 검정색, 신발: 흰색 운동화, 발생장소: 중앙시장, 경찰 연락"
    )
    facts, _ = parse_message(text)
    assert is_missing_alert(text)
    assert facts.name == "김○○"
    assert facts.gender == "여"
    assert facts.height == "153"
    assert facts.weight == "48"
    assert facts.top == "빨간색"
    assert facts.bottom == "검정색"
    assert facts.shoes == "흰색 운동화"
    assert facts.last_seen == "중앙시장"

