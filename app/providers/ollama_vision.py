import base64
import json

import httpx

from ..prompt import verification_prompt
from ..schemas import Appearance, Verification


class OllamaVisionVerifier:
    def __init__(self, base_url: str, model: str, mock: bool = False):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.mock = mock

    async def verify(self, image: bytes, appearance: Appearance) -> Verification:
        if self.mock:
            return Verification(passed=True, score=100)
        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "messages": [{
                "role": "user",
                "content": verification_prompt(appearance),
                "images": [base64.b64encode(image).decode("ascii")],
            }],
        }
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
        content = response.json()["message"]["content"]
        parsed = json.loads(content)
        return Verification.model_validate(parsed)

