# Training Guide

## Dataset Preparation

Organize images under `dataset/processed/` with one folder per class:

```
dataset/processed/
├── Healthy/
├── Bacterial Blight/
├── Anthracnose/
...
```

Or generate a synthetic demo dataset:

```bash
cd backend
python -m training.generate_dataset --samples 40 --output ../dataset/processed
```

### Preprocessing Pipeline

Implemented in `backend/training/preprocess.py`:

- Resize to 224×224
- Normalize pixels to [0, 1]
- Denoise (Non-local Means)
- Sharpen (kernel filter)
- Augmentation: rotation, horizontal/vertical flip, brightness, contrast, Gaussian noise
- Class balancing via oversampling (`balance_dataset_symlink`)

## Baseline CNN Training

```bash
cd backend
python -c "from training.train import train_baseline_cnn; train_baseline_cnn(epochs=10)"
```

Outputs:
- `models/best_model.keras`
- `static/metrics/cnn_baseline_metrics.json`
- Confusion matrix and ROC plots

## WOA-Optimized Training

```bash
python -c "from training.train import train_with_woa; train_with_woa(population_size=3, max_iterations=2)"
```

WOA searches: learning rate, batch size, filters, kernel size, dropout, dense units, epochs, optimizer, activation.

Comparison saved to `models/woa_comparison.json`.

## Hyperparameters (Default)

| Parameter | Default |
|-----------|---------|
| Image size | 224 |
| Batch size | 32 |
| Epochs | 50 |
| Learning rate | 0.001 |
| Dropout | 0.3 |
| Filters (base) | 32 |

## Model Architecture

```
Input → Conv2D → BatchNorm → ReLU → MaxPool → Dropout (×3 blocks)
     → Flatten → Dense → Dropout → Softmax(9)
```

Callbacks: EarlyStopping, ReduceLROnPlateau, ModelCheckpoint.
