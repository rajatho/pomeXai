"""API route handlers."""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    DashboardStats,
    HealthResponse,
    HistoryItem,
    ModelInfoResponse,
    PredictionResponse,
    RecommendationRequest,
)
from app.config import DISEASE_CLASSES, get_settings
from app.database.models import PredictionRecord, get_db
from app.recommendation.engine import build_diagnosis_payload, normalize_disease_name
from app.reports.pdf_generator import generate_pdf_report
from app.utils.predictor import predictor

router = APIRouter()
settings = get_settings()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/x-png"}


def _image_url(path: str) -> str:
    name = Path(path).name
    return f"/uploads/{name}"


def _validate_image_upload(file: UploadFile) -> None:
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    content_type = (file.content_type or "").lower()

    if ext not in ALLOWED_EXTENSIONS and content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid image. Only JPG, JPEG, and PNG files are supported.",
        )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    info = predictor.model_info()
    return HealthResponse(
        status="ok" if info["loaded"] else "degraded",
        app_name=settings.app_name,
        version=settings.app_version,
        model_loaded=bool(info["loaded"]),
        model_name=info.get("model_name"),
        classes=info.get("classes") or DISEASE_CLASSES,
        device=info.get("device"),
        best_val_accuracy=info.get("best_val_accuracy"),
    )


@router.get("/model-info", response_model=ModelInfoResponse)
async def model_info() -> ModelInfoResponse:
    info = predictor.model_info()
    return ModelInfoResponse(**info)


@router.get("/classes")
async def list_classes() -> dict:
    return {
        "classes": DISEASE_CLASSES,
        "count": len(DISEASE_CLASSES),
        "note": "Order matches ImageFolder / checkpoint class_to_idx",
    }


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)) -> dict:
    _validate_image_upload(file)

    upload_dir = Path(settings.resolved_upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "image.jpg").suffix.lower() or ".jpg"
    if ext not in ALLOWED_EXTENSIONS:
        ext = ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = upload_dir / filename

    content = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.max_upload_mb} MB.",
        )
    if not content:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    dest.write_bytes(content)
    return {
        "filename": filename,
        "path": str(dest),
        "url": f"/uploads/{filename}",
    }


@router.post("/predict", response_model=PredictionResponse)
async def predict_disease(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> PredictionResponse:
    upload_result = await upload_image(file)
    image_path = upload_result["path"]

    try:
        diagnosis = predictor.predict_from_path(image_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc

    report_path = None
    try:
        report_path = generate_pdf_report(diagnosis, image_path=image_path, gradcam_path=None)
    except Exception:
        report_path = None

    record = PredictionRecord(
        image_path=image_path,
        disease_name=diagnosis["disease_name"],
        confidence=diagnosis["confidence"],
        severity=diagnosis["severity"],
        affected_part=diagnosis["affected_part"],
        recommendations_json=json.dumps(diagnosis["recommendations"]),
        gradcam_path=None,
        report_path=report_path,
        created_at=datetime.utcnow(),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return PredictionResponse(
        id=record.id,
        image_path=image_path,
        image_url=upload_result["url"],
        report_path=report_path,
        created_at=record.created_at,
        **diagnosis,
    )


@router.post("/recommend")
async def recommend_fertilizer(payload: RecommendationRequest) -> dict:
    canonical = normalize_disease_name(payload.disease_name)
    known = set(DISEASE_CLASSES) | {
        "Bacterial Blight",
        "Cercospora Fruit Spot",
        "Alternaria",
        "Anthracnose",
        "Healthy",
    }
    if payload.disease_name not in known and canonical not in known:
        raise HTTPException(status_code=404, detail=f"Unknown disease: {payload.disease_name}")

    diagnosis = build_diagnosis_payload(payload.disease_name, confidence=0.75)
    return {
        "disease_name": payload.disease_name,
        "recommendations": diagnosis["recommendations"],
    }


@router.get("/history", response_model=List[HistoryItem])
async def prediction_history(
    limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = Query(None),
    disease: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> List[HistoryItem]:
    query = select(PredictionRecord).order_by(PredictionRecord.created_at.desc()).limit(limit)
    result = await db.execute(query)
    records = result.scalars().all()

    items: List[HistoryItem] = []
    for record in records:
        if disease and record.disease_name.lower() != disease.lower():
            continue
        if search and search.lower() not in record.disease_name.lower():
            continue
        items.append(
            HistoryItem(
                id=record.id,
                disease_name=record.disease_name,
                confidence=record.confidence,
                severity=record.severity,
                image_path=record.image_path,
                image_url=_image_url(record.image_path),
                created_at=record.created_at,
            )
        )
    return items


@router.get("/history/{record_id}", response_model=PredictionResponse)
async def prediction_detail(
    record_id: int,
    db: AsyncSession = Depends(get_db),
) -> PredictionResponse:
    result = await db.execute(
        select(PredictionRecord).where(PredictionRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail="Prediction not found")

    confidence_fraction = record.confidence / 100.0 if record.confidence > 1 else record.confidence
    diagnosis = build_diagnosis_payload(record.disease_name, confidence_fraction)
    diagnosis["confidence"] = record.confidence
    diagnosis["severity"] = record.severity

    recommendations = diagnosis["recommendations"]
    if record.recommendations_json:
        try:
            recommendations = json.loads(record.recommendations_json)
        except json.JSONDecodeError:
            pass

    return PredictionResponse(
        id=record.id,
        disease_name=record.disease_name,
        display_name=diagnosis.get("display_name"),
        confidence=record.confidence,
        severity=record.severity,
        affected_part=record.affected_part or diagnosis["affected_part"],
        description=diagnosis["description"],
        possible_causes=diagnosis["possible_causes"],
        environmental_conditions=diagnosis["environmental_conditions"],
        severity_detail=diagnosis["severity_detail"],
        recommendations=recommendations,
        probabilities=diagnosis.get("probabilities", {}),
        image_path=record.image_path,
        image_url=_image_url(record.image_path),
        report_path=record.report_path,
        created_at=record.created_at,
    )


@router.get("/dashboard", response_model=DashboardStats)
async def dashboard_stats(db: AsyncSession = Depends(get_db)) -> DashboardStats:
    total_result = await db.execute(select(func.count(PredictionRecord.id)))
    total = int(total_result.scalar() or 0)

    avg_result = await db.execute(select(func.avg(PredictionRecord.confidence)))
    avg_conf = float(avg_result.scalar() or 0.0)

    dist_result = await db.execute(
        select(PredictionRecord.disease_name, func.count(PredictionRecord.id))
        .group_by(PredictionRecord.disease_name)
    )
    class_distribution = {row[0]: int(row[1]) for row in dist_result.all()}

    conf_result = await db.execute(select(PredictionRecord.confidence))
    confidences = [float(row[0]) for row in conf_result.all()]
    buckets = {"0-50": 0, "50-70": 0, "70-85": 0, "85-95": 0, "95-100": 0}
    for conf in confidences:
        if conf < 50:
            buckets["0-50"] += 1
        elif conf < 70:
            buckets["50-70"] += 1
        elif conf < 85:
            buckets["70-85"] += 1
        elif conf < 95:
            buckets["85-95"] += 1
        else:
            buckets["95-100"] += 1

    recent_result = await db.execute(
        select(PredictionRecord).order_by(PredictionRecord.created_at.desc()).limit(8)
    )
    recent = [
        HistoryItem(
            id=r.id,
            disease_name=r.disease_name,
            confidence=r.confidence,
            severity=r.severity,
            image_path=r.image_path,
            image_url=_image_url(r.image_path),
            created_at=r.created_at,
        )
        for r in recent_result.scalars().all()
    ]

    return DashboardStats(
        total_predictions=total,
        average_confidence=round(avg_conf, 2),
        class_distribution=class_distribution,
        confidence_buckets=buckets,
        recent=recent,
        source="persistent_database",
    )
