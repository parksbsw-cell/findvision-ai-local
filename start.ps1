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
& $python -m streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8000 --server.headless true --browser.gatherUsageStats false
