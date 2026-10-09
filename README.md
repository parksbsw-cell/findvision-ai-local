# FindVision AI Local

기존 FindVision 저장소와 독립된 로컬 우선 버전입니다. 외부 이미지 API의 건당 크레딧 대신
사용자 PC의 NVIDIA GPU에서 이미지를 생성하고, 로컬 비전 모델이 최대 3회 검수합니다.

## 핵심 구조

- 규칙 기반 한국어 인상착의 추출: 원문에 없는 특징을 만들지 않음
- 실사 인물용 RealVisXL 로컬 이미지 생성: API 키와 건당 크레딧 불필요
- Ollama `qwen2.5vl:3b` 검수: 후보 3장의 배경·자세·의복·신발을 각각 확인하고 가장 가까운 결과 선택
- SQLite 익명 통계: 방문, 생성, 재방문, 리텐션
- FastAPI: 향후 Android 재난문자 공유 앱이 같은 API 사용
- 원문·생성 이미지는 통계 DB에 저장하지 않음

로컬 생성은 금전 크레딧을 소비하지 않지만 GPU 전기, 저장 공간과 실행 중인 PC가 필요합니다.
모든 생성형 모델에는 오류 가능성이 있으므로 결과를 실제 신원 확인 자료로 사용하면 안 됩니다.

## 개발 모드 실행

```powershell
py -3.11 -m venv .venv
.venv\Scripts\pip install -e ".[dev]"
$env:FINDVISION_MOCK_GENERATION="true"
.venv\Scripts\uvicorn app.main:app --reload
```

브라우저에서 `http://127.0.0.1:8000`을 엽니다. 개발 모드는 모델 대신 테스트 이미지를
사용하므로 UI와 분석·검수 흐름을 빠르게 확인할 수 있습니다.

## 실제 로컬 AI 준비

1. NVIDIA 드라이버와 CUDA 지원 PyTorch를 설치합니다.
2. `pip install -e ".[gpu]"`로 이미지 모델 의존성을 설치합니다.
3. Ollama 0.12.7 이상을 설치하고 `ollama pull qwen2.5vl:3b`를 실행합니다.
4. `.env.example`을 `.env`로 복사하고 `FINDVISION_MOCK_GENERATION=false`를 확인합니다.
5. 처음 생성할 때 `SG161222/RealVisXL_V4.0` FP16 모델 파일이 다운로드됩니다.

이 PC에는 CUDA 12.8용 PyTorch, RealVisXL V4.0 FP16, `qwen2.5vl:3b`가 설치되어 실제 생성까지
확인되었습니다. 이후에는 프로젝트 폴더에서 다음 명령으로 실행합니다.

```powershell
.\start.ps1
```

관리자 통계는 `http://127.0.0.1:8000/admin`에서 확인합니다. `.env`의
`FINDVISION_ADMIN_TOKEN` 값을 입력해야 하며 토큰은 브라우저에 저장하지 않습니다.

RTX 5060 8GB에서는 CPU offload를 사용하므로 VRAM 초과를 줄이는 대신 생성 시간이 늘어날 수 있습니다.

## 테스트

```powershell
.venv\Scripts\pytest -q
.venv\Scripts\ruff check .
```

## 다음 단계

- 50~100개 실제 형식의 익명화된 문자로 파서 회귀 시험
- FLUX 양자화 모델과 SDXL의 복잡한 의복 일치율 비교
- Android 공유 대상 앱: 문자 선택 → FindVision API 전달 → 이미지 알림 표시
- 여러 날짜의 실제 사용자로 7일·30일 코호트 리텐션 검증

