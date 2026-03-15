@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo [1/3] 正在启动后端 (FastAPI)...
start "AutoMeeting-Backend" cmd /k "cd /d "%~dp0backend" && (if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat) && pip install -q -r requirements.txt && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo [2/3] 等待后端就绪...
timeout /t 3 /nobreak >nul

echo [3/3] 正在启动前端 (Vite)...
cd frontend
if not exist node_modules (
  echo 首次运行：安装前端依赖...
  call npm install
)
call npm run dev

endlocal
