"""
Parallel Fan-out (並列ファンアウト) — launching independent subagents at once

When subtasks do not depend on each other, a coordinator can start them
concurrently instead of one after another.  Subagents are usually
latency-bound (they spend their time waiting on tool calls or model
responses), so running them in parallel threads collapses the total wait
to roughly the slowest single task rather than the sum of all of them.

This module models that with latency-bound workers and compares serial
execution against a thread pool, using only the standard library
(`concurrent.futures`).
"""

from __future__ import annotations
import time
from concurrent.futures import ThreadPoolExecutor

Task = tuple[str, float]                     # (name, simulated work seconds)


def subagent(task: Task) -> str:
    """A latency-bound worker: waits, then returns a one-line report."""
    name, seconds = task
    time.sleep(seconds)                      # stand-in for I/O / model latency
    return f"{name} done in {seconds:.2f}s"


def run_serial(tasks: list[Task]) -> tuple[list[str], float]:
    t0 = time.perf_counter()
    results = [subagent(t) for t in tasks]
    return results, time.perf_counter() - t0


def run_parallel(tasks: list[Task], max_workers: int) -> tuple[list[str], float]:
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        results = list(pool.map(subagent, tasks))
    return results, time.perf_counter() - t0


# ── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tasks: list[Task] = [
        ("search-docs", 0.30), ("read-config", 0.20), ("scan-tests", 0.40),
        ("lint-report", 0.25), ("build-index", 0.35),
    ]
    total = sum(s for _, s in tasks)
    print(f"{len(tasks)} independent subtasks, total work {total:.2f}s\n")

    _serial, t_serial = run_serial(tasks)
    print(f"Serial   : {t_serial:.2f}s  (waits add up)")

    results, t_par = run_parallel(tasks, max_workers=len(tasks))
    print(f"Parallel : {t_par:.2f}s  (bounded by the slowest task)")
    print(f"Speed-up : {t_serial / t_par:.1f}x\n")

    print("Reports (completion order not guaranteed):")
    for r in results:
        print(f"  {r}")

    print("\nFanning out independent subagents turns a sum of waits into a")
    print("single wait — the main reason a coordinator spawns them in parallel.")
