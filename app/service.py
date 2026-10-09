import asyncio
import base64
import secrets

import httpx

from .config import settings
from .parser import parse_message
from .prompt import image_prompt
from .providers.diffusers_local import LocalImageGenerator
from .providers.ollama_vision import OllamaVisionVerifier
from .schemas import Appearance, GenerateResponse, Verification

generator = LocalImageGenerator(settings.image_model, settings.mock_generation)
verifier = OllamaVisionVerifier(
    settings.ollama_url,
    settings.verifier_model,
    settings.mock_generation,
)


async def generate_verified(message: str, appearance: Appearance | None = None) -> GenerateResponse:
    if appearance is None:
        appearance, _ = parse_message(message)
    await verifier.unload()
    prompt = image_prompt(appearance)
    candidates = [
        await asyncio.to_thread(
            generator.generate,
            prompt,
            secrets.randbits(31),
            768,
            1024,
            30,
            7.5,
        )
        for _ in range(settings.max_attempts)
    ]
    generator.release_gpu_cache()
    best_image = candidates[0]
    best = Verification(passed=False, score=0, feedback="검수 결과 없음")
    attempts = 0
    try:
        for attempts, image in enumerate(candidates, 1):
            try:
                verdict = await verifier.verify(image, appearance)
            except (TimeoutError, ValueError, httpx.TimeoutException):
                verdict = Verification(
                    passed=False,
                    score=0,
                    wrong=["시각 검수가 제한 시간 안에 완료되지 않음"],
                    feedback="시각 검수가 제한 시간 안에 완료되지 않음",
                )
            if verdict.score >= best.score:
                best_image, best = image, verdict
    finally:
        await verifier.unload()
    return GenerateResponse(
        image_base64=base64.b64encode(best_image).decode("ascii"),
        attempts=attempts,
        verification=best,
        appearance=appearance,
    )

