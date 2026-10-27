"""Image preprocessing, augmentation, and dataset utilities."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Generator, List, Optional, Tuple

import cv2
import numpy as np
import tensorflow as tf
from sklearn.utils import class_weight
from tensorflow import keras

logger = logging.getLogger(__name__)


def preprocess_image(
    image: np.ndarray,
    target_size: Tuple[int, int] = (224, 224),
    sharpen: bool = True,
    denoise: bool = True,
) -> np.ndarray:
    """
    Preprocess a single BGR/RGB image for CNN inference.

    Steps: resize, denoise, sharpen, normalize to [0, 1].
    """
    if image is None or image.size == 0:
        raise ValueError("Invalid empty image")

    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    if image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

    resized = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)

    if denoise:
        resized = cv2.fastNlMeansDenoisingColored(resized, None, 10, 10, 7, 21)

    if sharpen:
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
        resized = cv2.filter2D(resized, -1, kernel)

    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    normalized = rgb.astype(np.float32) / 255.0
    return normalized


def load_image_from_path(path: str, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
    image = cv2.imread(path)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {path}")
    return preprocess_image(image, target_size=target_size)


def build_augmentation_layer() -> keras.Sequential:
    """Training-time data augmentation pipeline."""
    return keras.Sequential(
        [
            keras.layers.RandomRotation(0.15),
            keras.layers.RandomFlip("horizontal"),
            keras.layers.RandomFlip("vertical"),
            keras.layers.RandomBrightness(0.2),
            keras.layers.RandomContrast(0.2),
            keras.layers.GaussianNoise(0.05),
        ],
        name="augmentation",
    )


def create_tf_dataset(
    directory: str,
    img_size: Tuple[int, int] = (224, 224),
    batch_size: int = 32,
    validation_split: float = 0.2,
    subset: Optional[str] = None,
    seed: int = 42,
    augment: bool = False,
) -> tf.data.Dataset:
    """Create tf.data.Dataset from directory structure class folders."""
    dataset = keras.utils.image_dataset_from_directory(
        directory,
        labels="inferred",
        label_mode="categorical",
        class_names=None,
        color_mode="rgb",
        batch_size=batch_size,
        image_size=img_size,
        shuffle=True,
        seed=seed,
        validation_split=validation_split,
        subset=subset,
        interpolation="bilinear",
    )

    normalization = keras.layers.Rescaling(1.0 / 255.0)
    augmentation = build_augmentation_layer()

    def _map_fn(images, labels):
        images = normalization(images)
        if augment:
            images = augmentation(images, training=True)
        return images, labels

    return dataset.map(_map_fn, num_parallel_calls=tf.data.AUTOTUNE).prefetch(tf.data.AUTOTUNE)


def compute_class_weights_from_directory(directory: str) -> dict:
    """Compute balanced class weights from folder counts."""
    counts = {}
    for class_name in sorted(os.listdir(directory)):
        class_path = os.path.join(directory, class_name)
        if os.path.isdir(class_path):
            counts[class_name] = len([f for f in os.listdir(class_path) if _is_image(f)])

    if not counts:
        return {}

    labels = []
    for idx, (name, count) in enumerate(sorted(counts.items())):
        labels.extend([idx] * count)

    weights = class_weight.compute_class_weight(
        class_weight="balanced",
        classes=np.unique(labels),
        y=np.array(labels),
    )
    return {i: float(w) for i, w in enumerate(weights)}


def balance_dataset_symlink(source_dir: str, output_dir: str, target_per_class: Optional[int] = None) -> str:
    """
    Create a balanced dataset copy by oversampling minority classes.

    Uses file copy (not symlink) for Windows compatibility.
    """
    import shutil

    source = Path(source_dir)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    class_counts = {}
    for class_dir in sorted(source.iterdir()):
        if class_dir.is_dir():
            images = [f for f in class_dir.iterdir() if _is_image(f.name)]
            class_counts[class_dir.name] = images

    if not class_counts:
        raise ValueError(f"No class folders found in {source_dir}")

    max_count = target_per_class or max(len(v) for v in class_counts.values())

    for class_name, images in class_counts.items():
        dest = output / class_name
        dest.mkdir(parents=True, exist_ok=True)
        if not images:
            continue
        for i in range(max_count):
            src_file = images[i % len(images)]
            dst_file = dest / f"{src_file.stem}_{i}{src_file.suffix}"
            shutil.copy2(src_file, dst_file)

    logger.info("Balanced dataset written to %s (target %d per class)", output_dir, max_count)
    return str(output)


def _is_image(filename: str) -> bool:
    return filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp"))
