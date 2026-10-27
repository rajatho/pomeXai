"""Custom CNN architecture for pomegranate disease classification."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

logger = logging.getLogger(__name__)


def build_cnn_model(
    input_shape: Tuple[int, int, int] = (224, 224, 3),
    num_classes: int = 9,
    filters: int = 32,
    kernel_size: int = 3,
    dense_units: int = 128,
    dropout_rate: float = 0.3,
    activation: str = "relu",
    optimizer_name: str = "adam",
    learning_rate: float = 0.001,
) -> keras.Model:
    """
    Build a custom CNN for multi-class pomegranate disease detection.

    Architecture:
        Conv2D -> BatchNorm -> ReLU -> MaxPool -> Dropout (x3)
        -> Flatten -> Dense -> Dropout -> Softmax
    """
    inputs = keras.Input(shape=input_shape, name="input_image")

    x = inputs
    for i, f in enumerate([filters, filters * 2, filters * 4]):
        x = layers.Conv2D(
            f,
            kernel_size=kernel_size,
            padding="same",
            name=f"conv_{i + 1}",
        )(x)
        x = layers.BatchNormalization(name=f"bn_{i + 1}")(x)
        x = layers.Activation(activation, name=f"act_{i + 1}")(x)
        x = layers.MaxPooling2D(pool_size=2, name=f"pool_{i + 1}")(x)
        x = layers.Dropout(dropout_rate, name=f"dropout_conv_{i + 1}")(x)

    x = layers.Flatten(name="flatten")(x)
    x = layers.Dense(dense_units, activation=activation, name="dense_1")(x)
    x = layers.Dropout(dropout_rate, name="dropout_dense")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="pomegranate_cnn")

    optimizer = _get_optimizer(optimizer_name, learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="categorical_crossentropy",
        metrics=[
            "accuracy",
            keras.metrics.Precision(name="precision"),
            keras.metrics.Recall(name="recall"),
        ],
    )
    return model


def _get_optimizer(name: str, learning_rate: float) -> keras.optimizers.Optimizer:
    optimizers = {
        "adam": keras.optimizers.Adam(learning_rate=learning_rate),
        "sgd": keras.optimizers.SGD(learning_rate=learning_rate, momentum=0.9),
        "rmsprop": keras.optimizers.RMSprop(learning_rate=learning_rate),
        "adagrad": keras.optimizers.Adagrad(learning_rate=learning_rate),
    }
    key = name.lower()
    if key not in optimizers:
        logger.warning("Unknown optimizer %s, defaulting to Adam", name)
        return optimizers["adam"]
    return optimizers[key]


def get_callbacks(
    checkpoint_path: str,
    patience: int = 8,
) -> List[keras.callbacks.Callback]:
    """Return standard training callbacks."""
    return [
        keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=patience,
            restore_best_weights=True,
            verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1,
        ),
        keras.callbacks.ModelCheckpoint(
            filepath=checkpoint_path,
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
    ]


def hyperparameter_vector_to_config(vector: List[float], num_classes: int = 9) -> Dict[str, Any]:
    """
    Decode WOA search vector into CNN hyperparameters.

    Vector layout:
        [lr, batch_size, filters, kernel_size, dropout, dense_units, epochs, optimizer_idx, activation_idx]
    """
    optimizer_map = ["adam", "sgd", "rmsprop", "adagrad"]
    activation_map = ["relu", "elu", "selu"]

    lr = float(max(1e-5, min(vector[0], 0.1)))
    batch_size = int(max(8, min(round(vector[1]), 64)))
    filters = int(max(16, min(round(vector[2]), 128)))
    kernel_size = int(max(3, min(round(vector[3]), 7)))
    if kernel_size % 2 == 0:
        kernel_size += 1
    dropout = float(max(0.1, min(vector[4], 0.6)))
    dense_units = int(max(32, min(round(vector[5]), 512)))
    epochs = int(max(5, min(round(vector[6]), 50)))
    optimizer = optimizer_map[int(vector[7]) % len(optimizer_map)]
    activation = activation_map[int(vector[8]) % len(activation_map)]

    return {
        "learning_rate": lr,
        "batch_size": batch_size,
        "filters": filters,
        "kernel_size": kernel_size,
        "dropout_rate": dropout,
        "dense_units": dense_units,
        "epochs": epochs,
        "optimizer_name": optimizer,
        "activation": activation,
        "num_classes": num_classes,
    }


def save_model(model: keras.Model, path: str) -> None:
    model.save(path)
    logger.info("Model saved to %s", path)


def load_model(path: str) -> keras.Model:
    return keras.models.load_model(path)
