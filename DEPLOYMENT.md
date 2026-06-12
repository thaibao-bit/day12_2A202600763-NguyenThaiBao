# Deployment Information

## Public URL

https://ai-agent-production-8dcd.up.railway.app

## Platform

Railway.

## Test Commands

### Health Check

```bash
curl https://ai-agent-production-8dcd.up.railway.app/health
```

Expected:

```json
{"status":"ok"}
```

### API Test

```bash
curl -X POST https://ai-agent-production-8dcd.up.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"Hello"}'
```

### Rate Limit Test

```bash
for i in {1..15}; do
  curl -X POST https://ai-agent-production-8dcd.up.railway.app/ask \
    -H "X-API-Key: YOUR_KEY" \
    -H "Content-Type: application/json" \
    -d '{"user_id":"rate-test","question":"test"}'
done
```

Expected: requests after the first 10 in one minute return `429`.

## Environment Variables Set

- `PORT`
- `REDIS_URL` if Redis is attached; current Railway deployment uses the app's memory fallback.
- `AGENT_API_KEY`
- `JWT_SECRET`
- `RATE_LIMIT_PER_MINUTE=10`
- `MONTHLY_BUDGET_USD=10`
- `LOG_LEVEL` or platform logging defaults

## Screenshots

- Deployment dashboard: `screenshots/dashboard.png`
- Service running / health check: `screenshots/Heath.png`
- Test results: `screenshots/Ask.png`
