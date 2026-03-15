# 仅启动后端，供单独调试或先起后端再起前端时使用
$Root = $PSScriptRoot
Set-Location "$Root\backend"
if (Test-Path ".venv\Scripts\activate.ps1") { .\.venv\Scripts\Activate.ps1 }
Write-Host "正在检查/安装后端依赖..." -ForegroundColor Cyan
pip install -q -r requirements.txt
Write-Host "后端启动中: http://127.0.0.1:8000  文档: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
