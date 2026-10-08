from pydantic import BaseModel, Field


class Appearance(BaseModel):
    gender: str = ""
    age: str = ""
    height: str = ""
    weight: str = ""
    body_type: str = ""
    hair: str = ""
    top: str = ""
    outerwear: str = ""
    bottom: str = ""
    shoes: str = ""
    hat: str = ""
    glasses: str = ""
    facial_hair: str = ""
    accessories: list[str] = Field(default_factory=list)
    last_seen: str = ""


class AnalyzeRequest(BaseModel):
    message: str = Field(min_length=3, max_length=1800)


class AnalyzeResponse(BaseModel):
    is_missing_alert: bool
    appearance: Appearance
    warnings: list[str]


class GenerateRequest(AnalyzeRequest):
    appearance: Appearance | None = None


class Verification(BaseModel):
    passed: bool
    score: int = Field(ge=0, le=100)
    missing: list[str] = Field(default_factory=list)
    wrong: list[str] = Field(default_factory=list)
    feedback: str = ""


class GenerateResponse(BaseModel):
    image_base64: str
    mime_type: str = "image/png"
    attempts: int
    verification: Verification
    appearance: Appearance

