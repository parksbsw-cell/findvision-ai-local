from preview_logic import enhance_features_from_text


def test_recovers_core_demographics_and_hair_color_when_ai_omits_them():
    text = "실종 여성 72세, 키 155cm, 몸무게 58kg, 흰색 짧은 파마머리"
    facts = enhance_features_from_text({}, text, "")

    assert facts["gender"] == "여성"
    assert facts["age"] == "72세"
    assert facts["height"] == "155cm"
    assert facts["weight"] == "58kg"
    assert facts["hair_color"] == "흰색"


def test_parenthesized_gender_and_outerwear_are_not_misclassified():
    text = (
        "김영희(여, 72세), 키 158cm, 통통한 편, 짧은 회색 머리, "
        "빨간색 긴팔 재킷, 검은색 긴바지, 검은색 고무신, 안경 착용"
    )
    facts = enhance_features_from_text({}, text, "")

    assert facts["gender"] == "여성"
    assert facts["hair_length"] == "짧음"
    assert facts["outerwear"] == "빨간색 긴팔 재킷"
    assert facts["top"] == ""
