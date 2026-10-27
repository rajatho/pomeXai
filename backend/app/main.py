"""FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.predictions import router
from app.config import BASE_DIR, get_settings
from app.database.models import init_db
from app.utils.predictor import predictor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(settings.resolved_upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.resolved_reports_dir).mkdir(parents=True, exist_ok=True)
    Path(BASE_DIR / "database").mkdir(parents=True, exist_ok=True)
    Path(BASE_DIR / "models").mkdir(parents=True, exist_ok=True)

    await init_db()
    try:
        predictor.load()
        logger.info("PomeXAI FusionNet loaded successfully")
    except Exception as exc:
        logger.error("Model failed to load: %s", exc)

    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Pomegranate disease prediction using the trained PomeXAI FusionNet "
        "(ResNet50 + ViT gated fusion) checkpoint."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["predictions"])

upload_dir = Path(settings.resolved_upload_dir)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

static_root = BASE_DIR / "static"
static_root.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_root)), name="static")


@app.get("/")
async def root():
    return {
        "message": settings.app_name,
        "docs": "/docs",
        "health": "/api/v1/health",
        "model": "/api/v1/model-info",
    }
