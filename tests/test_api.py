from app.main import analyze, app
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

