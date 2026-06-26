import time
from typing import Any


class MetricsCollector:
    def __init__(self):
        self._starts: dict[str, float] = {}
        self.timings: dict[str, float] = {}
        self.tokens: dict[str, dict[str, int]] = {}

    def start_timer(self, key: str) -> None:
        self._starts[key] = time.perf_counter()

    def end_timer(self, key: str) -> float:
        start = self._starts.pop(key, None)
        elapsed = time.perf_counter() - start if start is not None else 0.0
        self.timings[key] = round(elapsed, 4)
        return self.timings[key]

    def record_tokens(self, agent: str, metadata: dict | None) -> None:
        meta = metadata or {}
        self.tokens[agent] = {
            "prompt_tokens": meta.get("prompt_tokens", 0),
            "completion_tokens": meta.get("completion_tokens", 0),
            "total_tokens": meta.get("total_tokens", 0),
        }

    def to_flat_row(self, patient_id: str, requested_agents: list[str]) -> dict[str, Any]:
        row: dict[str, Any] = {
            "patient_id": patient_id,
            "requested_agents": ",".join(requested_agents),
            "agent_count": len(requested_agents),
            "total_latency": self.timings.get("total", 0),
            "labs_latency": self.timings.get("labs"),
            "risk_latency": self.timings.get("risk"),
            "cost_latency": self.timings.get("cost"),
            "manager_latency": self.timings.get("manager", 0),
            "output_size_chars": None,
            "success": True,
            "error": None,
        }

        for agent in ("labs", "risk", "cost", "manager"):
            token_data = self.tokens.get(agent, {})
            row[f"{agent}_tokens_prompt"] = token_data.get("prompt_tokens")
            row[f"{agent}_tokens_completion"] = token_data.get("completion_tokens")
            row[f"{agent}_tokens_total"] = token_data.get("total_tokens")

        return row


def aggregate_results(rows: list[dict]) -> dict:
    successes = [row for row in rows if row.get("success")]

    return {
        "total_runs": len(rows),
        "successful_runs": len(successes),
        "failed_runs": len(rows) - len(successes),
        "avg_total_latency": round(
            sum(row["total_latency"] for row in successes) / len(successes), 4
        ) if successes else 0,
        "avg_tokens_by_agent": {
            agent: round(
                sum(row.get(f"{agent}_tokens_total") or 0 for row in successes) / len(successes),
                1,
            )
            for agent in ("labs", "risk", "cost", "manager")
        },
        "rows": rows,
    }
