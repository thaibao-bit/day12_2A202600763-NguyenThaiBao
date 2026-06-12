# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. Hardcoded database URLs and secrets make local examples unsafe for production.
2. Binding only to `localhost` prevents containers and cloud load balancers from reaching the service.
3. Debug mode and local-only assumptions are not appropriate for public deployment.
4. Configuration is embedded in code instead of being supplied through environment variables.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---|---|---|---|
| Config | Hardcoded/default local values | Environment variables | Keeps one image portable across environments |
| Secrets | Can appear directly in code | Supplied by platform secret manager/env | Prevents credential leaks |
| Host binding | `localhost` | `0.0.0.0` | Allows Docker/cloud networking |
| Logging | Human-readable console output | Structured logs | Easier to search and monitor |
| Health checks | Optional | `/health` and `/ready` | Enables automated restart and routing decisions |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: `python:3.11-slim`.
2. Working directory: `/app`.
3. Dependencies are installed from `requirements.txt`.
4. The production Dockerfile uses a builder stage and a runtime stage.
5. The app runs as a non-root `agent` user.

### Exercise 2.3: Image size comparison
- Develop: larger because dependencies and build tools stay in one image.
- Production: smaller because build tools remain in the builder stage.
- Difference: production multi-stage builds reduce attack surface and final image size.

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://ai-agent-production-8dcd.up.railway.app
- Screenshot: `screenshots/dashboard.png`

## Part 4: API Security

### Exercise 4.1-4.3: Test results
Expected local tests:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"Hello"}'
# Expected: 401 Unauthorized

curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: dev-key-change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"Hello"}'
# Expected: 200 OK
```

### Exercise 4.4: Cost guard implementation
The final app implements a monthly budget guard using Redis-backed counters. Usage cost is estimated from input/output token counts and blocked when the configured monthly budget is exhausted.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
The final project includes `/health`, `/ready`, graceful shutdown logging, Docker health checks, Redis-backed rate limiting, Redis-backed cost tracking, and environment-based configuration. Redis keeps request/cost state outside the application process so multiple workers or instances can share the same limits.
