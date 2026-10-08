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
    passed: bool = Field(description="True only when every required visual detail matches")
    score: int = Field(ge=0, le=100, description="Overall match percentage")
    missing: list[str] = Field(
        default_factory=list, description="Required details absent from the image"
    )
    wrong: list[str] = Field(
        default_factory=list,
        description="Only mismatched or extra visible details; never include correct details",
    )
    feedback: str = Field(default="", description="Short actionable correction")


class VisualCheck(BaseModel):
    requirement: str
    matches: bool
    observation: str


class GroupAudit(BaseModel):
    checks: list[VisualCheck]


class GenerateResponse(BaseModel):
    image_base64: str
    mime_type: str = "image/png"
    attempts: int
    verification: Verification
    appearance: Appearance

