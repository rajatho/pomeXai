"""Generate synthetic pomegranate disease dataset for training and demo."""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import cv2
import numpy as np

from app.config import DISEASE_CLASSES, BASE_DIR

PATTERNS = {
    "Healthy": {"base": (40, 120, 40), "spots": False},
    "Bacterial Blight": {"base": (50, 100, 45), "spots": True, "color": (20, 20, 20)},
    "Anthracnose": {"base": (45, 90, 35), "spots": True, "color": (30, 30, 80)},
    "Cercospora Fruit Spot": {"base": (55, 85, 50), "spots": True, "color": (80, 80, 80)},
    "Alternaria": {"base": (40, 70, 30), "spots": True, "color": (10, 10, 10), "rings": True},
    "Wilt Disease": {"base": (60, 90, 30), "spots": False, "wilt": True},
    "Leaf Spot": {"base": (35, 110, 35), "spots": True, "color": (40, 20, 20)},
    "Fruit Rot": {"base": (30, 40, 100), "spots": True, "color": (20, 20, 120), "rot": True},
    "Nutrient Deficiency": {"base": (80, 120, 40), "spots": False, "chlorosis": True},
}


def _draw_spots(img: np.ndarray, color: tuple, count: int = 15, rings: bool = False) -> None:
    h, w = img.shape[:2]
    for _ in range(count):
        cx, cy = random.randint(20, w - 20), random.randint(20, h - 20)
        radius = random.randint(5, 20)
        cv2.circle(img, (cx, cy), radius, color, -1)
        if rings:
            cv2.circle(img, (cx, cy), radius + 5, (0, 0, 0), 2)


def generate_image(class_name: str, size: int = 224) -> np.ndarray:
    cfg = PATTERNS[class_name]
    img = np.zeros((size, size, 3), dtype=np.uint8)
    img[:] = cfg["base"]

    noise = np.random.randint(-15, 15, img.shape, dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    if cfg.get("spots"):
        _draw_spots(img, cfg.get("color", (0, 0, 0)), rings=cfg.get("rings", False))

    if cfg.get("wilt"):
        cv2.line(img, (0, size // 2), (size, size // 2 + 30), (30, 60, 20), 8)

    if cfg.get("rot"):
        cv2.ellipse(img, (size // 2, size // 2), (60, 80), 0, 0, 360, (20, 20, 150), -1)

    if cfg.get("chlorosis"):
        img[: size // 2, :, 1] = np.clip(img[: size // 2, :, 1].astype(int) + 40, 0, 255)

    cv2.GaussianBlur(img, (5, 5), 0, dst=img)
    return img


def generate_dataset(output_dir: Path, samples_per_class: int = 40, img_size: int = 224) -> None:
    for class_name in DISEASE_CLASSES:
        class_dir = output_dir / class_name
        class_dir.mkdir(parents=True, exist_ok=True)
        safe = class_name.replace(" ", "_")
        for i in range(samples_per_class):
            image = generate_image(class_name, img_size)
            cv2.imwrite(str(class_dir / f"{safe}_{i:04d}.jpg"), image)
    print(f"Dataset generated at {output_dir} ({samples_per_class} samples x {len(DISEASE_CLASSES)} classes)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic pomegranate dataset")
    parser.add_argument("--output", default=str(BASE_DIR / "dataset" / "processed"))
    parser.add_argument("--samples", type=int, default=40)
    parser.add_argument("--size", type=int, default=224)
    args = parser.parse_args()
    random.seed(42)
    np.random.seed(42)
    generate_dataset(Path(args.output), args.samples, args.size)
