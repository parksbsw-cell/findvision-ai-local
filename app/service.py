import base64
import secrets

from .config import settings
from .parser import parse_message
from .prompt import image_prompt
from .providers.diffusers_local import LocalImageGenerator
from .providers.ollama_vision import OllamaVisionVerifier
from .schemas import Appearance, GenerateResponse, Verification

generator = LocalImageGenerator(settings.image_model, settings.mock_generation)
verifier = OllamaVisionVerifier(settings.ollama_url, settings.verifier_model, settings.mock_generation)


async def generate_verified(message: str, appearance: Appearance | None = None) -> GenerateResponse:
    if appearance is None:
        appearance, _ = parse_message(message)
    correction = ""
    best_image = b""
    best = Verification(passed=False, score=0, feedback="검수 결과 없음")
    attempts = 0
    for attempts in range(1, settings.max_attempts + 1):
        image = generator.generate(image_prompt(appearance, correction), secrets.randbits(31))
        verdict = await verifier.verify(image, appearance)
        if verdict.score >= best.score:
            best_image, best = image, verdict
        if verdict.passed:
            break
        correction = verdict.feedback or (
            "Add missing: " + ", ".join(verdict.missing) + ". Remove or fix: "
            + ", ".join(verdict.wrong)
        )
    return GenerateResponse(
        image_base64=base64.b64encode(best_image).decode("ascii"),
        attempts=attempts,
        verification=best,
        appearance=appearance,
    )

