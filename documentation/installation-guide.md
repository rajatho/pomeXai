# Installation Guide

## 1. Backend (PyTorch)

```powershell
cd C:\Users\ASUS\pomegranate-disease-detection\backend
python -m venv venv_torch
.\venv_torch\Scripts\activate
pip install -r requirements.txt
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install timm greenlet
```

Or use the prepared venv and launcher:

```powershell
cd C:\Users\ASUS\pomegranate-disease-detection
.\run_backend.bat
```

## 2. Frontend

```powershell
cd C:\Users\ASUS\pomegranate-disease-detection\frontend
npm install
npm run dev
```

Or:

```powershell
.\run_frontend.bat
```

## 3. Verify

1. http://localhost:8000/api/v1/health → `model_loaded: true`
2. http://localhost:5173 → Home shows model status
3. Upload a test image from the dataset `test/` folder and click Predict

## Troubleshooting

- **Model not found:** copy `PomeXAI_FusionNet_best.pt` into `models/`
- **greenlet error:** `pip install greenlet`
- **Slow first prediction:** normal on CPU while weights load into memory
- **Port in use:** change ports in uvicorn / Vite config
