"""Metrics visualization utilities."""

from __future__ import annotations

from typing import List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize


def plot_confusion_matrix(cm: np.ndarray, class_names: List[str], save_path: str) -> None:
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_names, yticklabels=class_names)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_roc_curves(y_true_cat: np.ndarray, y_prob: np.ndarray, class_names: List[str], save_path: str) -> None:
    n_classes = len(class_names)
    y_bin = label_binarize(np.argmax(y_true_cat, axis=1), classes=list(range(n_classes)))
    if n_classes == 2:
        y_bin = np.hstack([1 - y_prob[:, 1:2], y_prob[:, 1:2]])

    plt.figure(figsize=(10, 8))
    for i, name in enumerate(class_names):
        fpr, tpr, _ = roc_curve(y_bin[:, i], y_prob[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, label=f"{name} (AUC={roc_auc:.2f})")

    plt.plot([0, 1], [0, 1], "k--", alpha=0.5)
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curves")
    plt.legend(loc="lower right", fontsize=8)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_loss_curves(history: dict, save_path: str) -> None:
    plt.figure(figsize=(10, 5))
    if "loss" in history:
        plt.plot(history["loss"], label="Training Loss")
    if "val_loss" in history:
        plt.plot(history["val_loss"], label="Validation Loss")
    if "accuracy" in history:
        plt.plot(history["accuracy"], label="Training Accuracy")
    if "val_accuracy" in history:
        plt.plot(history["val_accuracy"], label="Validation Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Value")
    plt.title("Training Curves")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
