# Lab 12 - Complete Production Agent

This folder contains the final production-ready agent for Day 12.

## Checklist Deliverable

- [x] Multi-stage Dockerfile
- [x] Docker Compose stack with agent and Redis
- [x] `.dockerignore`
- [x] `GET /health`
- [x] `GET /ready`
- [x] API key authentication
- [x] Rate limiting: 10 requests/minute
- [x] Monthly cost guard: 10 USD/month
- [x] Config from environment variables
- [x] Structured logging
- [x] Graceful shutdown
- [x] Redis-backed shared state for rate/cost counters
- [x] Railway and Render config

## Structure

```text
06-lab-complete/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── auth.py
│   ├── rate_limiter.py
│   ├── cost_guard.py
│   └── redis_store.py
├── utils/
│   └── mock_llm.py
├── Dockerfile
├── docker-compose.yml
├── railway.toml
├── render.yaml
├── .env.example
├── .dockerignore
└── requirements.txt
```

## Run Locally

```bash
docker compose up --build
```

If port `8000` is already used, run:

```bash
HOST_PORT=18000 docker compose up --build
```

PowerShell:

```powershell
$env:HOST_PORT="18000"; docker compose up --build
```

Test health:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Test the agent:

```bash
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: dev-key-change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"What is deployment?"}'
```

Rate limit test:

```bash
for i in {1..15}; do
  curl -X POST http://localhost:8000/ask \
    -H "X-API-Key: dev-key-change-me-in-production" \
    -H "Content-Type: application/json" \
    -d '{"user_id":"rate-test","question":"test"}'
done
```

## Deploy Railway

```bash
npm i -g @railway/cli
railway login
railway init
railway variables set AGENT_API_KEY=your-secret-key
railway variables set JWT_SECRET=your-jwt-secret
railway variables set RATE_LIMIT_PER_MINUTE=10
railway variables set MONTHLY_BUDGET_USD=10
railway up
railway domain
```

## Deploy Render

1. Push this repository to GitHub.
2. In Render, create a new Blueprint from this repository.
3. Render reads `render.yaml`.
4. Add required secrets if prompted.
5. Deploy and copy the public URL to `DEPLOYMENT.md`.

## Production Readiness

```bash
python check_production_ready.py
```
