@echo off
chcp 65001 >nul
cd /d "%~dp0backend"
if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat
echo 正在检查/安装后端依赖...
pip install -q -r requirements.txt
echo 后端启动中: http://127.0.0.1:8000  文档: http://127.0.0.1:8000/docs
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
