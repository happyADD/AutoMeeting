# 一键启动：先启动后端，再启动前端
# 用法: .\start.ps1  或在 PowerShell 中: powershell -ExecutionPolicy Bypass -File .\start.ps1

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location $Root

Write-Host "[1/3] 正在启动后端 (FastAPI)..." -ForegroundColor Cyan
$backendJob = Start-Process -FilePath "cmd.exe" -ArgumentList '/k', "cd /d `"$Root\backend`" && (if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat) && pip install -q -r requirements.txt && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -PassThru -WindowStyle Normal

Write-Host "[2/3] 等待后端就绪..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

Write-Host "[3/3] 正在启动前端 (Vite)..." -ForegroundColor Cyan
Set-Location "$Root\frontend"
if (-not (Test-Path "node_modules")) {
    Write-Host "首次运行：安装前端依赖..." -ForegroundColor Yellow
    npm install
}
npm run dev
