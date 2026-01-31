# HPES Deployment Guide

## 1. Requirements
- Docker & Docker Compose
- Node.js 18+ (for frontend build)
- Python 3.10+ (for backend)

## 2. Environment Variables
Create a `.env` file in `backend/`:
```bash
DATABASE_URL=sqlite:///./data/hpes.db
SECRET_KEY=your_secret_key_change_in_prod
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 3. Production Build

### Backend
1. Build the Docker image:
   ```bash
   cd backend
   docker build -t hpes-backend .
   ```

2. Run with Gunicorn (Production Server):
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8002
   ```

### Frontend
1. Build static assets:
   ```bash
   cd frontend
   npm install
   npm run build
   ```
   
2. Serve `dist/` folder using Nginx.

## 4. Docker Compose (Recommended)
Use the provided `docker-compose.yml` to spin up the full stack:
```bash
docker-compose up -d --build
```

## 5. Monitoring
- Check logs: `docker logs -f hpes_backend`
- Health check: `curl http://localhost:8002/api/health`
