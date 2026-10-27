"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Central configuration for the pomegranate disease detection system."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=("settings_",),
    )

    app_name: str = "PomeXAI Disease Prediction"
    app_version: str = "2.0.0"
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"

    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR / 'database' / 'pomegranate.db'}"
    model_path: str = str(BASE_DIR / "models" / "PomeXAI_FusionNet_best.pt")
    img_size: int = 224
    num_classes: int = 5
    use_tta: bool = False
    max_upload_mb: int = 10

    upload_dir: str = str(BASE_DIR / "uploads")
    reports_dir: str = str(BASE_DIR / "static" / "reports")

    def resolve_path(self, path: str) -> str:
        p = Path(path)
        if not p.is_absolute():
            p = BASE_DIR / p
        return str(p)

    @property
    def resolved_model_path(self) -> str:
        return self.resolve_path(self.model_path)

    @property
    def resolved_upload_dir(self) -> str:
        return self.resolve_path(self.upload_dir)

    @property
    def resolved_reports_dir(self) -> str:
        return self.resolve_path(self.reports_dir)

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Exact class order stored in PomeXAI_FusionNet_best.pt
DISEASE_CLASSES = [
    "Alternaria",
    "Anthracnose",
    "Bacterial_Blight",
    "Cercospora",
    "Healthy",
]

CLASS_TO_INDEX = {name: idx for idx, name in enumerate(DISEASE_CLASSES)}
INDEX_TO_CLASS = {idx: name for name, idx in CLASS_TO_INDEX.items()}

# Friendly display labels for UI
DISPLAY_NAMES = {
    "Alternaria": "Alternaria",
    "Anthracnose": "Anthracnose",
    "Bacterial_Blight": "Bacterial Blight",
    "Cercospora": "Cercospora",
    "Healthy": "Healthy",
}
