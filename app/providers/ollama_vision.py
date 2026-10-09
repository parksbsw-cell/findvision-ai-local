import base64
import json

import httpx

from ..prompt import translate_terms
from ..schemas import Appearance, SceneAudit, Verification


class OllamaVisionVerifier:
    def __init__(self, base_url: str, model: str, mock: bool = False):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.mock = mock

    async def verify(self, image: bytes, appearance: Appearance) -> Verification:
        if self.mock:
            return Verification(passed=True, score=100)
        encoded = base64.b64encode(image).decode("ascii")
        prompt = (
            "Inspect only directly visible facts. Count people. Decide whether this is a real photograph, "
            "whether the background is completely empty and plain, whether either hand is hidden, touching "
            "a pocket, inside a pocket, or not fully visible beside the thighs, "
            "whether bottoms are shorts or ankle-length and their color, the top color and sleeve length, "
            "whether glasses are worn, the exact footwear category and color, whether outerwear is present, "
            "and list every extra accessory such as bags, hats, canes, umbrellas, jewelry, or watches."
        )
        payload = {
            "model": self.model,
            "stream": False,
            "keep_alive": "10m",
            "format": SceneAudit.model_json_schema(),
            "options": {"temperature": 0, "num_predict": 384},
            "messages": [{"role": "user", "content": prompt, "images": [encoded]}],
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            content = response.json()["message"].get("content", "").strip()
            if not content:
                raise ValueError("시각 검수 결과가 비어 있습니다.")
            scene = SceneAudit.model_validate(json.loads(content))

        wrong = []
        if scene.person_count != 1:
            wrong.append(f"한 명만 있어야 하지만 {scene.person_count}명 감지")
        if not scene.is_real_photo:
            wrong.append("실사 사진이 아닌 일러스트 또는 렌더링으로 감지")
        if not scene.plain_empty_background:
            wrong.append("비어 있는 단색 스튜디오 배경이 아님")
        if scene.hands_in_pockets:
            wrong.append("양손이 몸 옆에 완전히 보이지 않거나 주머니에 닿아 있음")
        bottom = translate_terms(appearance.bottom).lower()
        if ("trousers" in bottom or "long pants" in bottom) and scene.bottom_length != "ankle_length":
            wrong.append(f"긴바지 요구와 다름: {scene.bottom_length}")
        shoes = translate_terms(appearance.shoes).lower()
        if "clog" in shoes and "clog" not in scene.footwear_type.lower():
            wrong.append(f"클로그형 신발 요구와 다름: {scene.footwear_type}")
        if appearance.glasses and not scene.wears_glasses:
            wrong.append("안경이 보이지 않음")
        top = translate_terms(appearance.top).lower()
        if "short sleeve" in top and scene.top_sleeve != "short":
            wrong.append(f"반팔 요구와 다름: {scene.top_sleeve}")
        for color in ("black", "white", "gray", "brown", "navy", "blue", "red", "green", "yellow", "pink", "purple", "beige"):
            if color in top and color not in scene.top_color.lower():
                wrong.append(f"상의 색상 요구와 다름: {scene.top_color}")
                break
        if not appearance.outerwear and scene.outerwear_present:
            wrong.append("요청하지 않은 외투가 있음")
        score = max(0, 100 - min(90, len(wrong) * 12))
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

