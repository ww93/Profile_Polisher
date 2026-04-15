from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AgentContext:
    trace_id: str


class BaseAgent:
    name: str = "base"

    def run(self, *args, **kwargs):  # pragma: no cover - interface method
        raise NotImplementedError
