# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Project Overview

AutoMeeting is a counselor interview appointment booking and management system. It's a full-stack web application with:
- Backend: Python 3.10+, FastAPI, SQLAlchemy (async), SQLite/PostgreSQL
- Frontend: React 18 + Vite + TypeScript
- Email notification: SMTP integration

## Common Commands

### Backend
```bash
cd AutoMeeting/backend
pip install -r requirements.txt          # Install dependencies
python -m scripts.seed_db                # Initialize database with seed data
uvicorn app.main:app --reload --port 8000 # Start backend in development mode
pytest tests/ -v                         # Run backend unit tests
```

### Frontend
```bash
cd AutoMeeting/frontend
npm install                               # Install dependencies
npm run dev                               # Start development server (port 5173)
npm run build                             # Production build
npm run test:e2e                          # Run Playwright E2E tests
```

### One-click startup (Windows)
- `start.bat` - Windows CMD one-click startup
- `start.ps1` - PowerShell one-click startup

Scripts start backend first (port 8000), then frontend (port 5173).

## Code Architecture

```
AutoMeeting/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application entry point
│   │   ├── config.py        # Configuration loading
│   │   ├── db.py            # Database connection setup
│   │   ├── models/          # SQLAlchemy models (Counselor, SlotTemplate, Appointment)
│   │   ├── api/             # API routes (counselors, availability, appointments)
│   │   └── services/        # Business logic (availability checking, email)
│   ├── scripts/
│   │   └── seed_db.py       # Database initialization script
│   ├── tests/               # Backend unit tests
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/           # Page components (Calendar, Booking, Success, Admin)
│   │   ├── api/             # API client for backend calls
│   │   └── App.tsx          # Root component
│   ├── e2e/                 # Playwright E2E tests
│   └── package.json         # npm dependencies
└── .env.example             # Environment variables template
```

## Key Features

- **Calendar View**: Two-week display of available slots filterable by counselor
- **Booking System**: Form submission with conflict detection
- **Admin Dashboard** (`/admin`): Manage counselors, time slots, and appointments
- **Email Notifications**: SMTP integration to notify counselors of new appointments
- **Vite Proxy**: Frontend `/api` requests are proxied to backend on port 8000

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/counselors` | List all counselors |
| GET | `/availability` | Get available slots (query params: counselor_id, start_date, end_date) |
| POST | `/appointments` | Create new appointment |
| GET | `/appointments` | List appointments (optional filters) |

## Development Notes

- Frontend runs on port 5173, backend on port 8000
- Always start backend before frontend when developing manually
- Database URL and SMTP credentials are configured via environment variables in `.env`
- API documentation available at `http://localhost:8000/docs`
- For production: use PostgreSQL, backend with gunicorn/uvicorn, frontend built and served via Nginx
