# Deployment Guide

## Production Checklist

- [ ] Set `DEBUG=false` in `.env`
- [ ] Change `SECRET_KEY`
- [ ] Train model on real pomegranate dataset
- [ ] Configure PostgreSQL (optional) via `DATABASE_URL`
- [ ] Enable HTTPS reverse proxy (Nginx/Caddy)
- [ ] Build frontend: `npm run build`

## Backend (Production)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

Or with Gunicorn + Uvicorn workers:

```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## Frontend (Static Hosting)

```bash
cd frontend
npm run build
# Serve dist/ via Nginx or copy to CDN
```

Update Vite proxy or set `VITE_API_URL` if API is on a different domain.

## Docker (Optional)

Mount volumes for `models/`, `database/`, `uploads/`, `static/`.

## Environment Variables

See `.env.example` for all configurable values.
