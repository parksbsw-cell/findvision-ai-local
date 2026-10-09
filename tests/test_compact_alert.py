from preview_logic import enhance_features_from_text


def test_compact_comma_separated_alert_recovers_all_visual_facts():
    text = (
        "이름 구자운, 남,18세, 175CM,74KG, 검은색 반팔, "
        "검은색 바지, 검은색 크록스, 안경"
    )

    result = enhance_features_from_text({}, text, "")

    assert result["gender"] == "남성"
    assert result["age"] == "18세"
    assert result["height"] == "175cm"
    assert result["weight"] == "74kg"
    assert "검은색" in result["top"] and "반팔" in result["top"]
    assert "검은색" in result["bottom"] and "바지" in result["bottom"]
    assert "검은색" in result["shoes"] and "크록스" in result["shoes"]
    assert result["glasses"] == "안경"
