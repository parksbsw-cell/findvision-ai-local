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

