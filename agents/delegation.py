"""
Task Delegation (タスク委譲) — an orchestrator routing work to typed
specialist "subagents"

This mirrors how a coordinator hands a self-contained task to the right
specialist and receives back only a report — not the specialist's scratch
work.  Each subagent here:

  * declares a `kind` it handles (its "subagent type"),
  * sees *only* the task payload it is given (isolated context),
  * returns a structured report {agent, result, summary}.

The orchestrator picks a subagent by kind, runs it, and aggregates the
reports — exactly the shape of an agent that fans work out and relays the
conclusions, not the transcripts.
"""

from __future__ import annotations
import math
import statistics
from collections import Counter
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Report:
    agent: str
    result: Any
    summary: str


Task = dict[str, Any]                       # {"kind": str, "payload": ...}
Subagent = Callable[[Any], Report]


# ── Specialist subagents (each handles one kind of task) ──────────────────
def stats_agent(payload: list[float]) -> Report:
    mean = statistics.mean(payload)
    sd = statistics.pstdev(payload)
    result = {"n": len(payload), "mean": mean, "min": min(payload),
              "max": max(payload), "stdev": sd}
    return Report("stats", result,
                  f"{len(payload)} values, mean={mean:.2f}, stdev={sd:.2f}")


def wordfreq_agent(payload: str) -> Report:
    words = [w.strip(".,!?;:").lower() for w in payload.split()]
    top = Counter(w for w in words if w).most_common(3)
    return Report("wordfreq", top,
                  "top words: " + ", ".join(f"{w}({c})" for w, c in top))


def primes_agent(payload: int) -> Report:
    sieve = [True] * (payload + 1)
    for i in range(2, int(math.isqrt(payload)) + 1):
        if sieve[i]:
            for j in range(i * i, payload + 1, i):
                sieve[j] = False
    primes = [i for i in range(2, payload + 1) if sieve[i]]
    return Report("primes", len(primes),
                  f"{len(primes)} primes up to {payload} (largest {primes[-1]})")


# ── Orchestrator ──────────────────────────────────────────────────────────
class Orchestrator:
    def __init__(self) -> None:
        self._registry: dict[str, Subagent] = {}

    def register(self, kind: str, agent: Subagent) -> None:
        self._registry[kind] = agent

    def kinds(self) -> list[str]:
        return list(self._registry)

    def dispatch(self, task: Task) -> Report:
        kind = task["kind"]
        if kind not in self._registry:
            raise KeyError(f"no subagent registered for kind '{kind}'")
        return self._registry[kind](task["payload"])      # isolated handoff

    def run_batch(self, tasks: list[Task]) -> list[Report]:
        return [self.dispatch(t) for t in tasks]


# ── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    orch = Orchestrator()
    orch.register("stats", stats_agent)
    orch.register("wordfreq", wordfreq_agent)
    orch.register("primes", primes_agent)
    print(f"Orchestrator with {len(orch.kinds())} subagent types: "
          f"{', '.join(orch.kinds())}\n")

    tasks: list[Task] = [
        {"kind": "stats", "payload": [4.0, 8.0, 15.0, 16.0, 23.0, 42.0]},
        {"kind": "wordfreq", "payload": "the agent asks the agent to ask again"},
        {"kind": "primes", "payload": 100},
    ]

    reports = orch.run_batch(tasks)
    print("Reports relayed back to the orchestrator:")
    for r in reports:
        print(f"  [{r.agent:8s}] {r.summary}")

    print("\nThe orchestrator never sees each specialist's internal work —")
    print("only the returned report — just as a parent agent relays a")
    print("subagent's conclusion, not its transcript.")
