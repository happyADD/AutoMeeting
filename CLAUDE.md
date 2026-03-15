# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Project Overview

AutoMeeting is a counselor interview appointment booking and management system. It's a full-stack web application with:
- Backend: Python 3.10+, FastAPI, SQLAlchemy (async), SQLite/PostgreSQL
- Frontend: React 18 + Vite + TypeScript
- Email notification: SMTP integration
- Deployable to Vercel with GitHub Actions CI/CD

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

### Using Make (recommended)
```bash
make install       # Install all dependencies
make dev           # Start development servers
make test          # Run backend tests
make test-e2e      # Run E2E tests
make build         # Build for production
make docker-up     # Start Docker services (PostgreSQL + backend + frontend)
make docker-down   # Stop Docker services
make migrate       # Run database migration (SQLite -> PostgreSQL)
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
│   │   ├── config.py        # Configuration loading (PostgreSQL pool, CORS)
│   │   ├── db.py            # Database connection setup (pooling)
│   │   ├── models/          # SQLAlchemy models (Counselor, SlotTemplate, Appointment)
│   │   ├── api/             # API routes (counselors, availability, appointments)
│   │   └── services/        # Business logic (availability checking, email)
│   ├── scripts/
│   │   ├── seed_db.py       # Database initialization script
│   │   └── migrate_sqlite_to_postgres.py  # Migration script
│   ├── tests/               # Backend unit tests
│   ├── api/
│   │   └── index.py         # Vercel API entry point
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # React components (AlgorithmArt)
│   │   ├── pages/           # Page components (Calendar, Booking, Success, Admin)
│   │   ├── styles/          # CSS modules (responsive.css)
│   │   ├── api/             # API client for backend calls
│   │   └── App.tsx          # Root component
│   ├── e2e/                 # Playwright E2E tests
│   └── package.json         # npm dependencies
├── .github/
│   └── workflows/
│       ├── ci.yml           # CI pipeline (tests, lint, security)
│       └── cd.yml           # CD pipeline (Vercel deploy)
├── docker-compose.dev.yml   # Local development with PostgreSQL
├── vercel.json              # Vercel deployment config
├── Makefile                 # Development commands
└── .env.example             # Environment variables template
```

## Key Features

- **Calendar View**: Two-week display of available slots filterable by counselor
- **Booking System**: Form submission with conflict detection
- **Admin Dashboard** (`/admin`): Manage counselors, time slots, and appointments
- **Email Notifications**: SMTP integration to notify counselors of new appointments
- **Vite Proxy**: Frontend `/api` requests are proxied to backend on port 8000
- **Algorithm Art**: Decorative particle animation on calendar page
- **Responsive Design**: Mobile-first responsive CSS system
- **Vercel Deployment**: One-click deploy via GitHub Actions

## Database Configuration

### SQLite (Development)
```bash
DATABASE_URL=sqlite+aiosqlite:///./automeeting.db
```

### PostgreSQL (Production/Vercel)
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname
```

### Database Migration
```bash
# Export from SQLite
python -m scripts.migrate_sqlite_to_postgres --export

# Import to PostgreSQL
python -m scripts.migrate_sqlite_to_postgres --import --target "postgresql+..."

# Full migration
python -m scripts.migrate_sqlite_to_postgres --migrate --target "postgresql+..."
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection | SQLite local |
| `DB_POOL_SIZE` | PostgreSQL pool size | 5 |
| `DB_MAX_OVERFLOW` | PostgreSQL overflow | 10 |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | localhost:5173, localhost:3000 |
| `ENVIRONMENT` | dev/staging/production | development |
| `SMTP_*` | Email configuration | - |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/counselors` | List all counselors |
| GET | `/availability` | Get available slots (query params: counselor_id, start_date, end_date) |
| POST | `/appointments` | Create new appointment |
| GET | `/appointments` | List appointments (optional filters) |

## Vercel Deployment

1. Set up Vercel project and get tokens
2. Configure GitHub Secrets:
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`
3. Push to main branch triggers deployment

## Development Notes

- Frontend runs on port 5173, backend on port 8000
- Always start backend before frontend when developing manually
- Database URL and SMTP credentials are configured via environment variables in `.env`
- API documentation available at `http://localhost:8000/docs`
- For production: use PostgreSQL, backend with gunicorn/uvicorn, frontend built and served via Nginx
