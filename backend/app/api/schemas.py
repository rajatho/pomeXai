"""Pydantic schemas for API request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    id: Optional[int] = None
    disease_name: str
    display_name: Optional[str] = None
    confidence: float
    severity: str
    affected_part: str
    description: str
    possible_causes: List[str]
    environmental_conditions: List[str]
    severity_detail: str
    recommendations: Dict[str, Any]
    probabilities: Dict[str, float] = Field(default_factory=dict)
    explainability: Dict[str, Any] = Field(default_factory=dict)
    model_name: Optional[str] = None
    device: Optional[str] = None
    image_path: Optional[str] = None
    image_url: Optional[str] = None
    report_path: Optional[str] = None
    created_at: Optional[datetime] = None


class HistoryItem(BaseModel):
    id: int
    disease_name: str
    confidence: float
    severity: str
    image_path: str
    image_url: Optional[str] = None
    created_at: datetime


class DashboardStats(BaseModel):
    total_predictions: int
    average_confidence: float
    class_distribution: Dict[str, int]
    confidence_buckets: Dict[str, int]
    recent: List[HistoryItem]
    source: str = "persistent_database"


class RecommendationRequest(BaseModel):
    disease_name: str


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    model_loaded: bool
    model_name: Optional[str] = None
    classes: List[str] = Field(default_factory=list)
    device: Optional[str] = None
    best_val_accuracy: Optional[float] = None


class ModelInfoResponse(BaseModel):
    loaded: bool
    model_name: str
    model_path: str
    classes: List[str]
    img_size: int
    device: str
    best_val_accuracy: Optional[float] = None
    error: Optional[str] = None
