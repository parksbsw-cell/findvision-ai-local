import hashlib
import hmac
import secrets
import time
from collections import defaultdict

from fastapi import Cookie, FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .analytics import Analytics
from .config import settings
from .parser import is_missing_alert, parse_message
from .schemas import AnalyzeRequest, AnalyzeResponse, GenerateRequest, GenerateResponse
from .service import generate_verified

app = FastAPI(title="FindVision AI Local", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
analytics = Analytics(settings.data_dir / "analytics.db")
requests_by_visitor: dict[str, list[float]] = defaultdict(list)


def visitor_id(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def rate_limit(visitor: str) -> None:
    now = time.time()
    recent = [stamp for stamp in requests_by_visitor[visitor] if now - stamp < 3600]
    if len(recent) >= settings.rate_limit_per_hour:
        raise HTTPException(429, "시간당 생성 제한에 도달했습니다.")
    recent.append(now)
    requests_by_visitor[visitor] = recent


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'"
    )
    return response


@app.get("/")
def index(response: Response, fv_visitor: str | None = Cookie(default=None)):
    token = fv_visitor or secrets.token_urlsafe(24)
    response.set_cookie("fv_visitor", token, httponly=True, samesite="strict", max_age=31536000)
    analytics.record(visitor_id(token), "visit")
    return FileResponse("static/index.html")


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    appearance, warnings = parse_message(request.message)
    return AnalyzeResponse(
        is_missing_alert=is_missing_alert(request.message),
        appearance=appearance,
        warnings=warnings,
    )


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest, fv_visitor: str | None = Cookie(default=None)):
    if not is_missing_alert(request.message):
        raise HTTPException(422, "실종 재난문자 형식을 확인할 수 없습니다.")
    token = fv_visitor or "anonymous"
    hashed = visitor_id(token)
    rate_limit(hashed)
    result = await generate_verified(request.message, request.appearance)
    analytics.record(hashed, "generated")
    return result


@app.get("/api/admin/stats")
def stats(x_admin_token: str = Header(default="")):
    if not settings.admin_token or not hmac.compare_digest(x_admin_token, settings.admin_token):
        raise HTTPException(404, "찾을 수 없습니다.")
    return analytics.summary()


@app.get("/health")
def health():
    return {"ok": True, "local_models": True}

