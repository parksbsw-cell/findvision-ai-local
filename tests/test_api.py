import pytest
from fastapi import HTTPException

from app.main import analyze, app, stats
from app.schemas import AnalyzeRequest


def test_analyze_api_handler():
    response = analyze(
        AnalyzeRequest(message="실종 남성 81세, 검은색 고무신 착용, 발견 시 경찰서 연락")
    )
    assert response.is_missing_alert
    assert response.appearance.shoes == "검은색 고무신"


def test_required_routes_are_registered():
    paths = {route.path for route in app.routes}
    assert {"/", "/api/analyze", "/api/generate", "/api/admin/stats", "/health"} <= paths


def test_admin_stats_are_hidden_without_configured_secret():
    with pytest.raises(HTTPException) as error:
        stats("")
    assert error.value.status_code == 404

