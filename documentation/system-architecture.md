# System Architecture

## Overview

```text
┌──────────────────────┐      HTTPS/REST       ┌──────────────────────────┐
│  React + Vite UI     │ ───────────────────► │  FastAPI Backend         │
│  - Home / Upload     │                      │  - Upload validation     │
│  - Prediction result │ ◄─────────────────── │  - Preprocess + infer    │
│  - Dashboard/charts  │   JSON + image URLs  │  - SQLite history        │
└──────────────────────┘                      └────────────┬─────────────┘
                                                           │
                                                           ▼
                                              ┌──────────────────────────┐
                                              │  PomeXAI FusionNet (.pt) │
                                              │  ResNet50 + ViT + Gate   │
                                              │  Softmax 5-class output  │
                                              └──────────────────────────┘
```

## Components

1. **Frontend** — React SPA for upload, preview, prediction display, and dashboard charts (Chart.js).
2. **API layer** — FastAPI routes under `/api/v1` for health, predict, history, dashboard.
3. **Inference service** — Loads `PomeXAI_FusionNet_best.pt` once at startup and runs torch inference.
4. **Persistence** — SQLAlchemy + SQLite stores prediction records used by the dashboard.
5. **Recommendation engine** — Maps predicted class to fertilizer/treatment guidance.

## Data flow (prediction)

1. User selects JPG/PNG (drag-drop or file picker).
2. Frontend posts multipart form to `POST /api/v1/predict`.
3. Backend validates extension/content type and size.
4. Image is saved under `uploads/`.
5. PIL loads RGB image → resize 224 → ImageNet normalize.
6. FusionNet forward pass → softmax probabilities.
7. Top class + confidence returned; record saved to SQLite.
8. UI shows result charts; dashboard refreshes from real DB counts.

## Security notes

- Model file stays on the server (`models/`), never shipped to the browser.
- Upload whitelist: `.jpg`, `.jpeg`, `.png` only.
- Max upload size configurable via `MAX_UPLOAD_MB`.
