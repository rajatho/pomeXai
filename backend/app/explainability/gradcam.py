"""Grad-CAM and activation visualization for model explainability."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow import keras


def _find_last_conv_layer(model: keras.Model) -> str:
    for layer in reversed(model.layers):
        if isinstance(layer, keras.layers.Conv2D):
            return layer.name
        if isinstance(layer, keras.Model):
            try:
                return _find_last_conv_layer(layer)
            except ValueError:
                continue
    raise ValueError("No Conv2D layer found in model")


def generate_gradcam(
    model: keras.Model,
    image: np.ndarray,
    class_index: Optional[int] = None,
    output_dir: str = "./static/gradcam",
    alpha: float = 0.4,
) -> Tuple[str, np.ndarray]:
    """
    Generate Grad-CAM heatmap overlay for the predicted class.

    Returns path to saved overlay image and raw heatmap array.
    """
    if image.ndim == 3:
        batch = np.expand_dims(image, axis=0)
    else:
        batch = image

    conv_layer_name = _find_last_conv_layer(model)
    grad_model = keras.Model(
        inputs=model.input,
        outputs=[model.get_layer(conv_layer_name).output, model.output],
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(batch)
        if class_index is None:
            class_index = int(tf.argmax(predictions[0]))
        loss = predictions[:, class_index]

    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_outputs = conv_outputs[0]
    heatmap = tf.reduce_sum(tf.multiply(pooled_grads, conv_outputs), axis=-1)
    heatmap = np.maximum(heatmap.numpy(), 0)
    heatmap /= np.max(heatmap) + 1e-8

    heatmap_resized = cv2.resize(heatmap, (batch.shape[2], batch.shape[1]))
    heatmap_uint8 = np.uint8(255 * heatmap_resized)
    heatmap_color = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
    heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

    original = (batch[0] * 255).astype(np.uint8)
    overlay = (alpha * heatmap_color + (1 - alpha) * original).astype(np.uint8)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    filename = f"gradcam_{uuid.uuid4().hex[:12]}.png"
    full_path = out_path / filename

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].imshow(original)
    axes[0].set_title("Original")
    axes[0].axis("off")
    axes[1].imshow(heatmap_resized, cmap="jet")
    axes[1].set_title("Grad-CAM")
    axes[1].axis("off")
    axes[2].imshow(overlay)
    axes[2].set_title("Overlay")
    axes[2].axis("off")
    plt.tight_layout()
    plt.savefig(full_path, dpi=150, bbox_inches="tight")
    plt.close()

    return str(full_path), heatmap_resized


def generate_feature_maps(
    model: keras.Model,
    image: np.ndarray,
    layer_name: Optional[str] = None,
    max_maps: int = 16,
    output_dir: str = "./static/gradcam",
) -> str:
    """Visualize feature maps from a convolutional layer."""
    if image.ndim == 3:
        batch = np.expand_dims(image, axis=0)
    else:
        batch = image

    layer_name = layer_name or _find_last_conv_layer(model)
    feature_extractor = keras.Model(inputs=model.input, outputs=model.get_layer(layer_name).output)
    features = feature_extractor.predict(batch, verbose=0)[0]

    n = min(max_maps, features.shape[-1])
    cols = 4
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 2.5, rows * 2.5))
    axes = np.array(axes).reshape(-1)

    for i in range(n):
        axes[i].imshow(features[:, :, i], cmap="viridis")
        axes[i].axis("off")
        axes[i].set_title(f"Map {i + 1}", fontsize=8)

    for j in range(n, len(axes)):
        axes[j].axis("off")

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    filename = f"featuremaps_{uuid.uuid4().hex[:12]}.png"
    full_path = out_path / filename
    plt.suptitle(f"Feature Maps — {layer_name}")
    plt.tight_layout()
    plt.savefig(full_path, dpi=150, bbox_inches="tight")
    plt.close()
    return str(full_path)
