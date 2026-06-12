"""Monthly LLM budget guard backed by Redis."""
import calendar
import time

from fastapi import HTTPException

from app.config import settings
from app.redis_store import redis_store


PRICE_PER_1K_INPUT_TOKENS = 0.00015
PRICE_PER_1K_OUTPUT_TOKENS = 0.0006


class CostGuard:
    def __init__(self, monthly_budget_usd: float):
        self.monthly_budget_usd = monthly_budget_usd

    def _month_key(self, user_id: str) -> str:
        return f"cost:{time.strftime('%Y-%m')}:{user_id}"

    def _ttl_to_next_month(self) -> int:
        now = time.localtime()
        days = calendar.monthrange(now.tm_year, now.tm_mon)[1]
        next_month = time.strptime(
            f"{now.tm_year + (1 if now.tm_mon == 12 else 0)}-"
            f"{1 if now.tm_mon == 12 else now.tm_mon + 1}-01",
            "%Y-%m-%d",
        )
        return max(3600, int(time.mktime(next_month) - time.time()) or days * 86400)

    def check_budget(self, user_id: str) -> None:
        used = redis_store.get_float(self._month_key(user_id))
        if used >= self.monthly_budget_usd:
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "Monthly budget exceeded",
                    "used_usd": round(used, 6),
                    "budget_usd": self.monthly_budget_usd,
                    "resets_at": "first day of next month",
                },
            )

    def record_usage(self, user_id: str, input_tokens: int, output_tokens: int) -> dict:
        cost = (
            input_tokens / 1000 * PRICE_PER_1K_INPUT_TOKENS
            + output_tokens / 1000 * PRICE_PER_1K_OUTPUT_TOKENS
        )
        used = redis_store.incrbyfloat(self._month_key(user_id), cost, self._ttl_to_next_month())
        return {
            "user_id": user_id,
            "month": time.strftime("%Y-%m"),
            "cost_usd": round(used, 6),
            "budget_usd": self.monthly_budget_usd,
            "budget_remaining_usd": round(max(0.0, self.monthly_budget_usd - used), 6),
            "budget_used_pct": round(used / self.monthly_budget_usd * 100, 2),
        }

    def get_usage(self, user_id: str) -> dict:
        used = redis_store.get_float(self._month_key(user_id))
        return {
            "user_id": user_id,
            "month": time.strftime("%Y-%m"),
            "cost_usd": round(used, 6),
            "budget_usd": self.monthly_budget_usd,
            "budget_remaining_usd": round(max(0.0, self.monthly_budget_usd - used), 6),
            "budget_used_pct": round(used / self.monthly_budget_usd * 100, 2),
        }


cost_guard = CostGuard(settings.monthly_budget_usd)
