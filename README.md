# 谈话预约与查询管理系统 (AutoMeeting)

辅导员谈话预约与查询：日历展示可预约时段、按辅导员筛选、填写预约并落库，同时通过 SMTP 通知辅导员。

## 技术栈

- **后端**: Python 3.10+, FastAPI, SQLAlchemy (async), SQLite / PostgreSQL
- **前端**: React 18, Vite, TypeScript
- **邮件**: smtplib + 环境变量配置 SMTP

## 项目结构

```
AutoMeeting/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── models/       # Counselor, SlotTemplate, Appointment
│   │   ├── api/          # counselors, availability, appointments
│   │   └── services/     # availability, email
│   ├── scripts/seed_db.py
│   ├── tests/
│   └── requirements.txt
├── frontend/         # React + Vite 前端
│   ├── src/
│   │   ├── pages/        # 日历页、预约页、成功页、管理后台
│   │   ├── api/
│   │   └── App.tsx
│   ├── e2e/              # Playwright E2E
│   └── package.json
├── .env.example
└── README.md
```

## 快速开始

### 一键启动（推荐）

在项目根目录执行：

- **Windows (CMD)**：双击 `start.bat` 或在命令行运行 `start.bat`
- **Windows (PowerShell)**：`.\start.ps1`（若受限可先执行 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`）

脚本会按顺序：**先启动后端**（新窗口，端口 8000）→ 等待约 3 秒 → 再启动前端（当前窗口，端口 5173）。前端会把 `/api` 请求代理到后端，**若只单独运行前端而不启动后端，会出现 `ECONNREFUSED 127.0.0.1:8000`**，请务必先让后端运行。

首次使用前请先完成：
1. 后端：`cd backend` → `pip install -r requirements.txt` → `python -m scripts.seed_db`（初始化数据）
2. 前端依赖由脚本在首次运行时自动执行 `npm install`（若 `frontend/node_modules` 不存在）

---

### 1. 后端（手动）

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
cp ../.env.example .env   # 按需修改
python -m scripts.seed_db # 初始化辅导员与时段（首次）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档: http://127.0.0.1:8000/docs

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 http://127.0.0.1:5173 。前端通过 Vite 代理将 `/api` 转发到后端 8000 端口。

### 3. 环境变量

复制 `.env.example` 为 `backend/.env`（或项目根目录 `.env`，依 `config` 加载方式）。必填一般只需 `DATABASE_URL`；要发邮件则配置 `SMTP_*`。

## 功能说明

- **管理后台**（`/admin`）：辅导员增删改查（工号、姓名、邮箱、启用/停用）、可预约时段增删改查（上午/下午、小时）、预约记录查看与取消。预约页头部提供「管理后台」入口。
- **日历与筛选**: 选择辅导员后展示两周内可预约时段（上午/下午按小时）；点击「可约」进入预约表单并带入时间。
- **预约表单**: 填写日期、时段、小时、内容、联系人及电话/邮箱；提交前校验，后端做冲突检测。
- **存储与邮件**: 预约写入数据库，并调用 SMTP 向辅导员邮箱发送通知（若已配置）。

## 测试

### 后端

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

### E2E（需先启动后端）

```bash
# 终端 1
cd backend && uvicorn app.main:app --port 8000

# 终端 2
cd frontend && npm install && npx playwright install chromium
npm run test:e2e
```

## 常见问题

- **`[vite] http proxy error: /counselors` 或 `ECONNREFUSED 127.0.0.1:8000`**  
  前端在请求接口时连不上后端。解决：先启动后端（端口 8000），再访问前端。  
  - 推荐直接使用**一键启动**（`start.bat` / `start.ps1`），会先起后端再起前端。  
  - 若分开启动：先在项目根目录运行 `start-backend.bat`（或 `.\start-backend.ps1`），等后端起来后再在 `frontend` 目录运行 `npm run dev`。

## 部署说明

- **后端**: 使用 gunicorn + uvicorn worker 或 Docker 部署；生产环境建议使用 PostgreSQL，并设置 `DATABASE_URL`。
- **前端**: `npm run build` 后将 `dist/` 部署到 Nginx 或其他静态托管；通过 Nginx 将 `/api` 反向代理到后端。
- **安全**: SMTP 密码、数据库 URL 等仅通过环境变量注入，勿提交到仓库。

## API 概要

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /counselors | 辅导员列表 |
| GET | /availability?counselor_id=&start_date=&end_date= | 某辅导员在日期范围内的空闲时段 |
| POST | /appointments | 创建预约（body: counselor_id, date, period, hour, content, contact_name, contact_phone/email） |
| GET | /appointments | 预约列表（可选 counselor_id, start_date, end_date） |
