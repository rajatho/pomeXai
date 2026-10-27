# API Documentation

Base URL: `http://localhost:8000/api/v1`

Interactive Swagger UI: `http://localhost:8000/docs`

## POST /predict

Upload an image and receive full diagnosis.

**Request:** `multipart/form-data` with field `file` (image)

**Response:**
```json
{
  "disease_name": "Anthracnose",
  "confidence": 87.5,
  "severity": "Severe",
  "affected_part": "Fruit / Leaf",
  "description": "...",
  "recommendations": { "fertilizer": "...", "npk_ratio": "8-12-20" },
  "probabilities": { "Healthy": 2.1, "Anthracnose": 87.5 },
  "explainability": { "gradcam_path": "/static/gradcam/...", "method": "Grad-CAM" },
  "report_path": "/static/reports/diagnosis_report_....pdf"
}
```

## POST /recommend

**Body:** `{ "disease_name": "Leaf Spot" }`

## GET /history?limit=50

Returns array of past predictions.

## GET /metrics

Returns baseline CNN and WOA-optimized CNN comparison metrics.

## GET /health

Service status and model load state.
