"""FastAPI app entry: CORS, router mount, init_db."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import init_db, seed_db
from app.api import counselors, calendar, appointments, slot_templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_db()
    yield
    # shutdown if needed
    pass


settings = get_settings()

app = FastAPI(
    title="谈话预约与查询管理系统",
    lifespan=lifespan,
)

# Dynamic CORS configuration based on environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(counselors.router, prefix="/api")
app.include_router(calendar.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(slot_templates.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "谈话预约与查询管理系统 API", "docs": "/docs"}
