# Testing Guide

## Unit Tests

```bash
cd backend
pytest -v
```

Tests cover:
- Recommendation engine for all disease classes
- Severity computation
- WOA optimization convergence

## Manual API Testing

```bash
# Health
curl http://localhost:8000/api/v1/health

# Predict
curl -X POST http://localhost:8000/api/v1/predict \
  -F "file=@../dataset/processed/Healthy/Healthy_0000.jpg"

# History
curl http://localhost:8000/api/v1/history
```

## Frontend Testing

1. Start backend and frontend
2. Upload a pomegranate image on `/upload`
3. Verify prediction cards, charts, Grad-CAM on `/prediction`
4. Check fertilizer and treatment pages
5. Download PDF report
6. Confirm entry appears in `/history`

## Expected Metrics (After Training)

Baseline and WOA metrics available at `GET /api/v1/metrics` and in `static/metrics/`.
