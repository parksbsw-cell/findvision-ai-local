from preview_logic import enhance_features_from_text


def test_recovers_core_demographics_and_hair_color_when_ai_omits_them():
    text = "실종 여성 72세, 키 155cm, 몸무게 58kg, 흰색 짧은 파마머리"
    facts = enhance_features_from_text({}, text, "")

    assert facts["gender"] == "여성"
    assert facts["age"] == "72세"
    assert facts["height"] == "155cm"
    assert facts["weight"] == "58kg"
    assert facts["hair_color"] == "흰색"
