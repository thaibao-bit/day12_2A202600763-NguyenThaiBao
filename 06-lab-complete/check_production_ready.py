"""Production readiness checker for the Day 12 complete lab."""
import os
import sys


def check(name: str, passed: bool, detail: str = "") -> dict:
    icon = "OK" if passed else "FAIL"
    print(f"  [{icon}] {name}" + (f" - {detail}" if detail else ""))
    return {"name": name, "passed": passed}


def contains(path: str, *needles: str) -> bool:
    if not os.path.exists(path):
        return False
    content = open(path, encoding="utf-8").read().lower()
    return all(needle.lower() in content for needle in needles)


def run_checks() -> bool:
    results = []
    base = os.path.dirname(__file__)

    print("\n" + "=" * 55)
    print("  Production Readiness Check - Day 12 Lab")
    print("=" * 55)

    print("\nRequired files")
    for filename in [
        "Dockerfile",
        "docker-compose.yml",
        ".dockerignore",
        ".env.example",
        "requirements.txt",
        "README.md",
    ]:
        results.append(check(f"{filename} exists", os.path.exists(os.path.join(base, filename))))

    results.append(check(
        "railway.toml or render.yaml exists",
        os.path.exists(os.path.join(base, "railway.toml")) or os.path.exists(os.path.join(base, "render.yaml")),
    ))

    print("\nApplication modules")
    for filename in [
        "app/main.py",
        "app/config.py",
        "app/auth.py",
        "app/rate_limiter.py",
        "app/cost_guard.py",
        "app/redis_store.py",
        "utils/mock_llm.py",
    ]:
        results.append(check(f"{filename} exists", os.path.exists(os.path.join(base, filename))))

    print("\nSecurity and configuration")
    root_gitignore = os.path.join(base, "..", ".gitignore")
    env_ignored = contains(root_gitignore, ".env")
    results.append(check(".env ignored by git", env_ignored))

    secret_hits = []
    for filename in ["app/main.py", "app/config.py", "app/auth.py"]:
        path = os.path.join(base, filename)
        if os.path.exists(path):
            content = open(path, encoding="utf-8").read()
            for bad in ["sk-", "password123", "hardcoded"]:
                if bad in content:
                    secret_hits.append(f"{filename}:{bad}")
    results.append(check("No obvious hardcoded secrets", not secret_hits, str(secret_hits)))
    results.append(check("Rate limit is 10/min", contains(os.path.join(base, ".env.example"), "RATE_LIMIT_PER_MINUTE=10")))
    results.append(check("Monthly budget is 10 USD", contains(os.path.join(base, ".env.example"), "MONTHLY_BUDGET_USD=10")))

    print("\nAPI behavior in code")
    main_py = os.path.join(base, "app", "main.py")
    results.append(check("/health endpoint defined", contains(main_py, '@app.get("/health"')))
    results.append(check("/ready endpoint defined", contains(main_py, '@app.get("/ready"')))
    results.append(check("/ask endpoint defined", contains(main_py, '@app.post("/ask"')))
    results.append(check("Authentication dependency used", contains(main_py, "verify_api_key")))
    results.append(check("Rate limiter used", contains(main_py, "rate_limiter.check")))
    results.append(check("Cost guard used", contains(main_py, "cost_guard")))
    results.append(check("Graceful shutdown signal configured", contains(main_py, "SIGTERM")))
    results.append(check("Structured logging present", contains(main_py, "json.dumps")))

    print("\nDocker")
    dockerfile = os.path.join(base, "Dockerfile")
    results.append(check("Multi-stage build", contains(dockerfile, "AS builder", "AS runtime")))
    results.append(check("Non-root user", contains(dockerfile, "USER agent")))
    results.append(check("HEALTHCHECK instruction", contains(dockerfile, "HEALTHCHECK")))
    results.append(check("Slim base image", contains(dockerfile, "python:3.11-slim")))
    results.append(check("Docker Compose includes Redis", contains(os.path.join(base, "docker-compose.yml"), "redis:7-alpine")))

    passed = sum(1 for item in results if item["passed"])
    total = len(results)
    pct = round(passed / total * 100)

    print("\n" + "=" * 55)
    print(f"  Result: {passed}/{total} checks passed ({pct}%)")
    print("  PRODUCTION READY" if pct == 100 else "  Fix failed items before submission")
    print("=" * 55 + "\n")
    return pct == 100


if __name__ == "__main__":
    sys.exit(0 if run_checks() else 1)
