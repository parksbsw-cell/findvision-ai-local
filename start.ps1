$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

if (-not $env:HF_HOME) {
    $env:HF_HOME = "C:\fvai-models"
}

$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "가상환경이 없습니다. README의 실제 로컬 AI 준비 단계를 먼저 실행하세요."
}

Write-Host "FindVision AI: http://127.0.0.1:8000"
Write-Host "관리자 통계: http://127.0.0.1:8000/admin"
& $python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
