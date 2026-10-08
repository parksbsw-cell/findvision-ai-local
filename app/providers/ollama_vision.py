import base64
import json

import httpx

from ..prompt import translate_terms
from ..schemas import Appearance, GroupAudit, Verification


class OllamaVisionVerifier:
    def __init__(self, base_url: str, model: str, mock: bool = False):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.mock = mock

    @staticmethod
    def _groups(appearance: Appearance) -> list[tuple[str, list[str]]]:
        age = f"{appearance.age} years old" if appearance.age else ""
        groups = [
            ("person and body", [appearance.gender, age, appearance.body_type, appearance.hair]),
            ("clothing and layers", [
                appearance.top, appearance.outerwear, appearance.bottom, appearance.hat,
            ]),
            ("footwear and carried items", [
                appearance.shoes, appearance.glasses, appearance.facial_hair,
                *appearance.accessories,
            ]),
        ]
        return [
            (name, [translate_terms(value) for value in values if value])
            for name, values in groups
        ]

    async def verify(self, image: bytes, appearance: Appearance) -> Verification:
        if self.mock:
            return Verification(passed=True, score=100)
        encoded = base64.b64encode(image).decode("ascii")
        checks = []
        async with httpx.AsyncClient(timeout=180) as client:
            for group_name, requirements in self._groups(appearance):
                if group_name == "footwear and carried items":
                    requirements.append("no unrequested backpack, bag, or extra accessory")
                numbered = "\n".join(
                    f"{number}. {requirement}" for number, requirement in enumerate(requirements, 1)
                )
                prompt = (
                    f"Inspect only {group_name}. Return exactly one check for every numbered line. "
                    "Set matches=false for an absent detail, different color/type, or forbidden "
                    "extra item. State only what is visibly observed.\n" + numbered
                )
                payload = {
                    "model": self.model,
                    "stream": False,
                    "format": GroupAudit.model_json_schema(),
                    "options": {"temperature": 0, "num_predict": 512},
                    "messages": [{"role": "user", "content": prompt, "images": [encoded]}],
                }
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                content = response.json()["message"].get("content", "").strip()
                if not content:
                    raise ValueError(f"{group_name} 검수 결과가 비어 있습니다.")
                audit = GroupAudit.model_validate(json.loads(content))
                checks.extend(audit.checks)

        expected = sum(len(values) for _, values in self._groups(appearance)) + 1
        failures = [check for check in checks if not check.matches]
        omitted = max(0, expected - len(checks))
        score = round(100 * max(0, len(checks) - len(failures)) / expected)
        wrong = [f"{check.requirement}: {check.observation}" for check in failures]
        if omitted:
            wrong.append(f"검수 모델이 {omitted}개 요구사항을 확인하지 못함")
        return Verification(
            passed=not wrong and score >= 90,
            score=score,
            missing=[],
            wrong=wrong,
            feedback="; ".join(wrong),
        )

