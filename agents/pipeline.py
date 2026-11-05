"""
Agent Pipeline (エージェント・パイプライン) — chaining single-purpose agents

Not all multi-agent work is parallel.  Often each agent does one job and
passes its output to the next: draft, then critique, then revise.  Giving
every stage a single responsibility keeps each one simple and testable,
and the hand-offs between them explicit — the sequential counterpart to
fanning work out.

This toy pipeline improves a numeric guess at the square root of a target:
a *proposer* suggests a value, a *critic* measures its error, and a
*reviser* applies one Newton step.  The loop stops when the critic is
satisfied, and the chain of hand-offs is printed.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable


@dataclass
class Message:
    value: float
    note: str


# ── Single-purpose agents ─────────────────────────────────────────────────
def proposer(target: float) -> Message:
    """Cold-start guess (deliberately rough)."""
    return Message(target, f"initial guess {target:.3f}")


def critic(msg: Message, target: float) -> tuple[bool, float]:
    """Judge the current value; return (accept?, signed error)."""
    error = msg.value * msg.value - target
    return abs(error) < 1e-9, error


def reviser(msg: Message, target: float) -> Message:
    """One Newton step toward sqrt(target): x <- (x + target/x) / 2."""
    x = (msg.value + target / msg.value) / 2
    return Message(x, f"newton step -> {x:.6f}")


def run_pipeline(target: float, proposer: Callable[[float], Message],
                 max_rounds: int = 20) -> Message:
    msg = proposer(target)
    print(f"  proposer: {msg.note}")
    for rnd in range(1, max_rounds + 1):
        accepted, error = critic(msg, target)
        print(f"  critic  : value={msg.value:.6f}  error={error:+.2e}"
              f"{'  (accepted)' if accepted else ''}")
        if accepted:
            break
        msg = reviser(msg, target)
        print(f"  reviser : {msg.note}")
    return msg


# ── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    target = 2.0
    print(f"Pipeline: proposer -> critic -> reviser, solving sqrt({target})\n")
    final = run_pipeline(target, proposer)
    print(f"\nFinal value: {final.value:.9f}")
    print(f"math.sqrt  : {target ** 0.5:.9f}")
    print("\nEach agent does one job; the critic gates the loop and the value")
    print("flows stage to stage — a sequential chain rather than a fan-out.")
