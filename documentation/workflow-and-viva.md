# Workflow, Features, Limitations & Future Work

## Prediction workflow

1. Start backend (`uvicorn`) → model loads from `models/PomeXAI_FusionNet_best.pt`.
2. Start frontend (`npm run dev`).
3. Open Home → confirm model status badge.
4. Go to Predict → upload image → click **Predict**.
5. View predicted class, confidence, probability charts, and treatment links.
6. Open Dashboard → inspect totals, distribution, confidence buckets, and history filters.

## Key features

- Reuses the **existing trained** FusionNet checkpoint (no retraining required).
- Exact training preprocessing (224 + ImageNet normalization).
- Real confidence scores from softmax (no mock predictions).
- Persistent SQLite history + separate temporary session history.
- Dashboard charts driven only by stored prediction records.
- Treatment recommendations mapped to predicted disease class.
- PDF diagnosis report generation.

## Limitations

- First model load is memory/CPU heavy (~400+ MB checkpoint).
- Domain shift: photos unlike the Roboflow training set may reduce reliability.
- Dashboard starts empty until real predictions are made.
- Explainability heatmap is not enabled in the default mini-project path.
- Single-model inference (ensemble/TTA available in research notebooks but optional here).

## Future enhancements

- Optional Grad-CAM overlay for FusionNet’s ResNet branch.
- GPU acceleration and batch upload.
- Farmer mobile PWA + offline caching.
- Active learning loop for hard examples.
- Multilingual treatment guidance.
- Role-based admin analytics.
