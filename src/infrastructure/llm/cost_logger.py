"""LLM cost logging and tracking."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class LLMCostLogger:
    """LLM xarajatlarini log qilish."""

    def __init__(self, log_file: str = "llm_costs.jsonl"):
        self.log_file = Path(log_file)

    def log_call(
        self,
        provider: str,
        model: str,
        task_type: str,
        tokens_used: int,
        cost_usd: float,
        user_id: str | None = None,
        extra: dict | None = None,
    ) -> None:
        """LLM chaqiruvini log qilish."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": provider,
            "model": model,
            "task_type": task_type,
            "tokens_used": tokens_used,
            "cost_usd": cost_usd,
            "user_id": user_id,
        }

        if extra:
            entry.update(extra)

        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        logger.info(
            f"LLM Call: {provider}/{model} — {tokens_used} tokens, ${cost_usd:.4f}"
        )

    def get_daily_costs(self, date: str | None = None) -> dict:
        """Kunlik xarajatlarni hisoblash."""
        if date is None:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        total_cost = 0.0
        total_tokens = 0
        calls = 0

        if self.log_file.exists():
            with open(self.log_file) as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("timestamp", "").startswith(date):
                            total_cost += entry.get("cost_usd", 0)
                            total_tokens += entry.get("tokens_used", 0)
                            calls += 1
                    except json.JSONDecodeError:
                        continue

        return {
            "date": date,
            "total_cost_usd": total_cost,
            "total_tokens": total_tokens,
            "calls": calls,
        }


cost_logger = LLMCostLogger()
