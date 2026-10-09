from streamlit_app import _local_visitor_key


def test_local_visitor_key_is_stable_and_does_not_expose_uuid():
    raw = "8f2506b4-5e17-4d2e-a985-79ba0ef86a8e"
    first = _local_visitor_key(raw)
    second = _local_visitor_key(raw)

    assert first == second
    assert raw not in first
    assert len(first) == 64
