from streamlit_app import build_generation_prompt, sync_prompt_text_from_structured_features


def test_clothing_and_possessions_precede_secondary_appearance():
    features = {
        "gender": "여성",
        "age": "72",
        "height": "155cm",
        "weight": "65kg",
        "body_type": "통통한 편",
        "hair_color": "흰색",
        "hair_style": "짧은 파마머리",
        "outerwear": "빨간색 패딩",
        "bottom": "남색 긴바지",
        "shoes": "흰색 운동화",
        "accessories": "오른손에 갈색 지팡이",
    }

    synced = sync_prompt_text_from_structured_features(features)
    description = synced["image_prompt_en"]
    assert description.index("outerwear: red puffer jacket") < description.index("body type:")
    assert description.index("accessories: in the right hand brown walking cane") < description.index("hair color:")

    prompt = build_generation_prompt(features, "")
    assert "MANDATORY CLOTHING AND ITEMS: OUTERWEAR: solid red puffer jacket" in prompt
    assert "no logo, emblem, badge, letters, numbers or decorative mark" in prompt
