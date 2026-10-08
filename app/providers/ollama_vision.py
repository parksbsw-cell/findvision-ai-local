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
        requirements = [
            requirement
            for _, group_requirements in self._groups(appearance)
            for requirement in group_requirements
        ]
        requirements.insert(0, "exactly one person shown once in one single full-body view")
        requirements.append("no unrequested backpack, bag, outerwear, or extra accessory")
        numbered = "\n".join(
            f"{number}. {requirement}" for number, requirement in enumerate(requirements, 1)
        )
        prompt = (
            f"Inspect the image carefully. There are exactly {len(requirements)} numbered tests. "
            "Return exactly that many checks, in the same order, copying each numbered requirement verbatim. "
            "Set matches=false for an absent detail, different color/type, or forbidden extra item. "
            "Gray does not match black. Shorts do not match pants. Sandals or sneakers do not "
            "match Crocs-style clogs. A collage or repeated person fails the final no-extra check. "
            "A white or gray shirt does not match a black shirt. A slide or open-toe sandal is not a clog. "
            "Age only needs to look like the stated age group. State only visible observations.\n"
            + numbered
        )
        payload = {
            "model": self.model,
            "stream": False,
            "keep_alive": "10m",
            "format": GroupAudit.model_json_schema(),
            "options": {"temperature": 0, "num_predict": 768},
            "messages": [{"role": "user", "content": prompt, "images": [encoded]}],
        }
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            content = response.json()["message"].get("content", "").strip()
            if not content:
                raise ValueError("시각 검수 결과가 비어 있습니다.")
            checks = GroupAudit.model_validate(json.loads(content)).checks

        expected = len(requirements)
        valid_order = len(checks) == expected and all(
            check.requirement.strip() == requirements[index].strip()
            for index, check in enumerate(checks[:expected])
        )
        failures = [check for check in checks if not check.matches]
        omitted = max(0, expected - len(checks))
        score = round(100 * max(0, len(checks) - len(failures)) / expected)
        wrong = [f"{check.requirement}: {check.observation}" for check in failures]
        if omitted:
            wrong.append(f"검수 모델이 {omitted}개 요구사항을 확인하지 못함")
        if not valid_order:
            wrong.append("검수 모델이 요구사항 전체를 정해진 순서로 확인하지 못함")
        return Verification(
            passed=not wrong and score >= 90,
            score=score,
            missing=[],
            wrong=wrong,
            feedback="; ".join(wrong),
        )

    async def unload(self) -> None:
        if self.mock:
            return
        async with httpx.AsyncClient(timeout=30) as client:
            await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "keep_alive": 0},
            )

