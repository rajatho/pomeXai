# PomeXAI — Pomegranate Disease Prediction Mini Project

End-to-end MCA mini project that runs **real inference** with your trained **PomeXAI FusionNet** checkpoint (`PomeXAI_FusionNet_best.pt`).

- **Frontend:** React + Vite + Tailwind CSS + Chart.js  
- **Backend:** FastAPI + PyTorch + timm  
- **Model:** ResNet50 + ViT gated fusion (5 classes)  
- **Storage:** SQLite prediction history (persistent) + browser `sessionStorage` (temporary)

## Findings (model discovery)

| Item | Value |
|------|-------|
| Checkpoint | `models/PomeXAI_FusionNet_best.pt` |
| Framework | PyTorch (not Keras/TF) |
| Architecture | `PomeXAI_FusionNet` |
| Classes | `Alternaria`, `Anthracnose`, `Bacterial_Blight`, `Cercospora`, `Healthy` |
| Input size | 224×224 RGB |
| Preprocessing | Resize → ToTensor → ImageNet normalize `(0.485, 0.456, 0.406)` / `(0.229, 0.224, 0.225)` |
| Checkpoint val accuracy | ~99.71% (stored in checkpoint metadata) |

Google Drive was **not** accessed. The checkpoint was found locally in `Downloads` and copied into `models/`.

## Project structure

```
pomegranate-disease-detection/
├── frontend/                 # React UI (upload, results, dashboard)
├── backend/                  # FastAPI inference API
│   ├── app/
│   │   ├── api/              # Routes + schemas
│   │   ├── models/           # FusionNet architecture
│   │   ├── utils/            # Predictor service
│   │   ├── recommendation/   # Treatment knowledge base
│   │   ├── database/         # SQLite models
│   │   └── reports/          # PDF generation
│   └── requirements.txt
├── models/                   # Trained .pt checkpoint (keep out of git if large)
├── documentation/            # Architecture, workflow, viva notes
├── uploads/                  # Uploaded inference images
├── database/                 # SQLite DB
└── static/reports/           # Generated PDF reports
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- ~2 GB free RAM for FusionNet CPU inference

## Setup

### 1. Model file

Ensure this file exists:

```
models/PomeXAI_FusionNet_best.pt
```

If missing, copy your trained checkpoint:

```powershell
Copy-Item "$env:USERPROFILE\Downloads\PomeXAI_FusionNet_best.pt" `
  ".\models\PomeXAI_FusionNet_best.pt"
```

### 2. Backend

```powershell
cd backend
python -m venv venv_torch
.\venv_torch\Scripts\activate
pip install -r requirements.txt
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install timm
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or double-click `run_backend.bat` from the project root.

API docs: http://localhost:8000/docs  
Health: http://localhost:8000/api/v1/health

### 3. Frontend

```powershell
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health + model status |
| GET | `/api/v1/model-info` | Checkpoint metadata |
| GET | `/api/v1/classes` | Class list |
| POST | `/api/v1/upload` | Secure image upload |
| POST | `/api/v1/predict` | Run FusionNet inference |
| GET | `/api/v1/history` | Persistent history (`search`, `disease` filters) |
| GET | `/api/v1/history/{id}` | Single stored result |
| GET | `/api/v1/dashboard` | Real stats for charts |
| POST | `/api/v1/recommend` | Treatment recommendations |

## Session vs permanent history

- **Permanent:** every successful `/predict` is stored in SQLite (`database/pomegranate.db`) and powers the dashboard.
- **Session:** the frontend also mirrors recent results in `sessionStorage` (`pomexai_session_history`). This clears when the browser tab closes and is shown separately on the dashboard.

## Documentation

See `documentation/` for:

- System architecture diagram
- Prediction workflow
- Key features, limitations, future enhancements
- Installation / viva notes

## Limitations

- CPU inference for FusionNet can take several seconds on first load.
- Grad-CAM is optional and not required for core prediction.
- Model quality depends on image quality and domain similarity to the training set.
- No fabricated accuracy claims beyond checkpoint metadata.

## License

Academic / MCA mini-project use.
