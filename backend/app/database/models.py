"""SQLAlchemy database models and session management."""

from __future__ import annotations

from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url, echo=settings.debug)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class PredictionRecord(Base):
    """Stored prediction history entry."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String(512), nullable=False)
    disease_name = Column(String(128), nullable=False)
    confidence = Column(Float, nullable=False)
    severity = Column(String(32), nullable=False)
    affected_part = Column(String(128))
    recommendations_json = Column(Text)
    gradcam_path = Column(String(512))
    report_path = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
