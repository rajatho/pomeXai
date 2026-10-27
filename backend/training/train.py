"""Training pipeline for baseline CNN and WOA-optimized CNN."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from tensorflow import keras

from app.config import BASE_DIR, DISEASE_CLASSES, get_settings
from app.models.cnn_model import build_cnn_model, get_callbacks, hyperparameter_vector_to_config
from app.utils.metrics import plot_confusion_matrix, plot_loss_curves, plot_roc_curves
from training.preprocess import compute_class_weights_from_directory, create_tf_dataset
from woa.whale_optimization import WhaleOptimizationAlgorithm, default_woa_bounds

logger = logging.getLogger(__name__)
settings = get_settings()


def _collect_labels_and_probs(
    model: keras.Model,
    dataset: tf.data.Dataset,
) -> Tuple[np.ndarray, np.ndarray]:
    y_true, y_prob = [], []
    for batch_x, batch_y in dataset:
        preds = model.predict(batch_x, verbose=0)
        y_prob.append(preds)
        y_true.append(batch_y.numpy())
    return np.vstack(y_true), np.vstack(y_prob)


def evaluate_model(
    model: keras.Model,
    test_dataset: tf.data.Dataset,
    class_names: list,
    output_dir: Path,
    prefix: str = "cnn",
) -> Dict[str, Any]:
    """Compute metrics and save evaluation plots."""
    y_true_cat, y_prob = _collect_labels_and_probs(model, test_dataset)
    y_true = np.argmax(y_true_cat, axis=1)
    y_pred = np.argmax(y_prob, axis=1)

    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)
    cm = confusion_matrix(y_true, y_pred)

    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "specificity": _specificity(cm),
        "sensitivity": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
    }

    try:
        if len(class_names) > 2:
            metrics["auc"] = float(
                roc_auc_score(y_true_cat, y_prob, multi_class="ovr", average="weighted")
            )
        else:
            metrics["auc"] = float(roc_auc_score(y_true, y_prob[:, 1]))
    except Exception as exc:
        logger.warning("AUC computation failed: %s", exc)
        metrics["auc"] = 0.0

    output_dir.mkdir(parents=True, exist_ok=True)
    plot_confusion_matrix(cm, class_names, str(output_dir / f"{prefix}_confusion_matrix.png"))
    plot_roc_curves(y_true_cat, y_prob, class_names, str(output_dir / f"{prefix}_roc_curve.png"))

    with open(output_dir / f"{prefix}_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    return metrics


def _specificity(cm: np.ndarray) -> float:
    specs = []
    for i in range(cm.shape[0]):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        tn = cm.sum() - tp - fp - fn
        denom = tn + fp
        specs.append(tn / denom if denom else 0.0)
    return float(np.mean(specs))


def train_baseline_cnn(
    dataset_path: Optional[str] = None,
    epochs: Optional[int] = None,
    batch_size: Optional[int] = None,
    img_size: int = 224,
) -> Dict[str, Any]:
    """Train baseline CNN without WOA."""
    dataset_path = dataset_path or settings.resolved_dataset_path
    epochs = epochs or settings.epochs
    batch_size = batch_size or settings.batch_size
    img_size_tuple = (img_size, img_size)

    train_ds = create_tf_dataset(
        dataset_path, img_size_tuple, batch_size, subset="training", augment=True
    )
    val_ds = create_tf_dataset(
        dataset_path, img_size_tuple, batch_size, subset="validation", augment=False
    )

    class_names = train_ds.class_names if hasattr(train_ds, "class_names") else DISEASE_CLASSES
    num_classes = len(class_names)

    model = build_cnn_model(
        input_shape=(img_size, img_size, 3),
        num_classes=num_classes,
        learning_rate=settings.learning_rate,
    )

    models_dir = BASE_DIR / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = str(models_dir / "best_model.keras")

    start = time.time()
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=get_callbacks(checkpoint),
        verbose=1,
    )
    training_time = time.time() - start

    metrics = evaluate_model(model, val_ds, class_names, BASE_DIR / "static" / "metrics", prefix="cnn_baseline")
    metrics["training_time_seconds"] = training_time
    metrics["final_val_loss"] = float(min(history.history["val_loss"]))
    metrics["final_val_accuracy"] = float(max(history.history["val_accuracy"]))

    plot_loss_curves(history.history, str(BASE_DIR / "static" / "metrics" / "cnn_baseline_loss.png"))

    with open(BASE_DIR / "models" / "baseline_history.json", "w", encoding="utf-8") as f:
        json.dump(history.history, f, indent=2)

    return {"model_path": checkpoint, "metrics": metrics, "class_names": class_names}


def train_with_woa(
    dataset_path: Optional[str] = None,
    population_size: Optional[int] = None,
    max_iterations: Optional[int] = None,
    img_size: int = 224,
) -> Dict[str, Any]:
    """Optimize CNN hyperparameters with WOA then train final model."""
    dataset_path = dataset_path or settings.resolved_dataset_path
    population_size = population_size or settings.woa_population_size
    max_iterations = max_iterations or settings.woa_max_iterations
    img_size_tuple = (img_size, img_size)

    train_ds_full = create_tf_dataset(
        dataset_path, img_size_tuple, 32, subset="training", augment=False
    )
    val_ds_full = create_tf_dataset(
        dataset_path, img_size_tuple, 32, subset="validation", augment=False
    )
    class_names = DISEASE_CLASSES
    num_classes = len(class_names)

    bounds = default_woa_bounds()
    woa = WhaleOptimizationAlgorithm(
        dim=len(bounds),
        bounds=bounds,
        population_size=population_size,
        max_iterations=max_iterations,
    )

    def fitness_fn(vector: np.ndarray) -> float:
        config = hyperparameter_vector_to_config(vector.tolist(), num_classes=num_classes)
        batch_size = config["batch_size"]
        train_ds = create_tf_dataset(
            dataset_path, img_size_tuple, batch_size, subset="training", augment=True
        )
        val_ds = create_tf_dataset(
            dataset_path, img_size_tuple, batch_size, subset="validation", augment=False
        )

        model = build_cnn_model(
            input_shape=(img_size, img_size, 3),
            num_classes=num_classes,
            filters=config["filters"],
            kernel_size=config["kernel_size"],
            dense_units=config["dense_units"],
            dropout_rate=config["dropout_rate"],
            activation=config["activation"],
            optimizer_name=config["optimizer_name"],
            learning_rate=config["learning_rate"],
        )

        history = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=config["epochs"],
            verbose=0,
            callbacks=[
                keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True)
            ],
        )
        val_acc = max(history.history["val_accuracy"])
        val_loss = min(history.history["val_loss"])
        fitness = -(val_acc) + 0.5 * val_loss
        keras.backend.clear_session()
        return float(fitness)

    woa_start = time.time()
    result = woa.optimize(fitness_fn)
    woa_time = time.time() - woa_start

    best = result.best_config
    train_ds = create_tf_dataset(
        dataset_path, img_size_tuple, best["batch_size"], subset="training", augment=True
    )
    val_ds = create_tf_dataset(
        dataset_path, img_size_tuple, best["batch_size"], subset="validation", augment=False
    )

    final_model = build_cnn_model(
        input_shape=(img_size, img_size, 3),
        num_classes=num_classes,
        filters=best["filters"],
        kernel_size=best["kernel_size"],
        dense_units=best["dense_units"],
        dropout_rate=best["dropout_rate"],
        activation=best["activation"],
        optimizer_name=best["optimizer_name"],
        learning_rate=best["learning_rate"],
    )

    models_dir = BASE_DIR / "models"
    woa_checkpoint = str(models_dir / "best_model_woa.keras")
    train_start = time.time()
    history = final_model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=settings.epochs,
        callbacks=get_callbacks(woa_checkpoint),
        verbose=1,
    )
    train_time = time.time() - train_start

    woa_metrics = evaluate_model(
        final_model, val_ds, class_names, BASE_DIR / "static" / "metrics", prefix="cnn_woa"
    )
    woa_metrics["woa_search_time_seconds"] = woa_time
    woa_metrics["training_time_seconds"] = train_time
    woa_metrics["final_val_loss"] = float(min(history.history["val_loss"]))
    woa_metrics["final_val_accuracy"] = float(max(history.history["val_accuracy"]))
    woa_metrics["best_hyperparameters"] = best

    plot_loss_curves(history.history, str(BASE_DIR / "static" / "metrics" / "cnn_woa_loss.png"))

    comparison_path = BASE_DIR / "models" / "woa_comparison.json"
    baseline_path = BASE_DIR / "static" / "metrics" / "cnn_baseline_metrics.json"
    comparison = {"woa": woa_metrics, "best_config": best, "convergence": result.convergence_curve}
    if baseline_path.exists():
        with open(baseline_path, encoding="utf-8") as f:
            comparison["baseline"] = json.load(f)

    with open(comparison_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2)

    return {
        "model_path": woa_checkpoint,
        "metrics": woa_metrics,
        "woa_result": {
            "best_fitness": result.best_fitness,
            "best_config": best,
            "convergence_curve": result.convergence_curve,
        },
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Training baseline CNN...")
    baseline = train_baseline_cnn()
    print(json.dumps(baseline["metrics"], indent=2))
    print("Running WOA optimization...")
    woa_out = train_with_woa()
    print(json.dumps(woa_out["metrics"], indent=2))
