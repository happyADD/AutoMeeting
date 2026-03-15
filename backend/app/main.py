"""FastAPI app entry: CORS, router mount, init_db."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.api import counselors, calendar, appointments, slot_templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    # shutdown if needed
    pass


app = FastAPI(
    title="谈话预约与查询管理系统",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(counselors.router)
app.include_router(calendar.router)
app.include_router(appointments.router)
app.include_router(slot_templates.router)


@app.get("/")
async def root():
    return {"message": "谈话预约与查询管理系统 API", "docs": "/docs"}
