"""
Agent-Based Market Simulation (エージェントベース市場シミュレーション)

A frontier of computational economics: instead of solving equations,
simulate many interacting agents and observe emergent aggregates.

Two experiments:
1. Wealth exchange — random pairwise trades produce an unequal wealth
   distribution (measured by the Gini coefficient) from equal starts.
2. Zero-intelligence double auction (Gode & Sunder, 1993) — traders
   bidding at random still drive prices toward the equilibrium implied
   by their private values.
"""

from __future__ import annotations
import random
from dataclasses import dataclass


def gini(wealths: list[float]) -> float:
    """Gini coefficient: 0 = perfect equality, 1 = maximal inequality."""
    xs = sorted(wealths)
    n = len(xs)
    total = sum(xs)
    if total == 0:
        return 0.0
    weighted = sum((i + 1) * x for i, x in enumerate(xs))
    return (2 * weighted) / (n * total) - (n + 1) / n


def wealth_exchange(n_agents: int, rounds: int, rng: random.Random) -> list[float]:
    """Random-transfer economy: each round, a random pair splits a
    random fraction of the poorer agent's wealth."""
    wealth = [100.0] * n_agents
    for _ in range(rounds):
        i, j = rng.sample(range(n_agents), 2)
        stake = rng.random() * min(wealth[i], wealth[j])
        if rng.random() < 0.5:
            wealth[i] += stake
            wealth[j] -= stake
        else:
            wealth[i] -= stake
            wealth[j] += stake
    return wealth


@dataclass
class Trader:
    limit: float   # private value (buyer) or cost (seller)


def double_auction(buyers: list[Trader], sellers: list[Trader],
                   rounds: int, rng: random.Random) -> list[float]:
    """Zero-intelligence traders: bids/asks are uniform random within
    each trader's budget constraint. Returns transaction prices."""
    prices: list[float] = []
    active_buyers = list(buyers)
    active_sellers = list(sellers)
    for _ in range(rounds):
        if not active_buyers or not active_sellers:
            break
        buyer = rng.choice(active_buyers)
        seller = rng.choice(active_sellers)
        bid = rng.uniform(0, buyer.limit)          # never bid above value
        ask = rng.uniform(seller.limit, 200)       # never ask below cost
        if bid >= ask:
            prices.append((bid + ask) / 2)
            active_buyers.remove(buyer)
            active_sellers.remove(seller)
    return prices


def theoretical_equilibrium(buyers: list[Trader], sellers: list[Trader]) -> float:
    """Midpoint of the marginal traders' limits where supply meets demand."""
    values = sorted((b.limit for b in buyers), reverse=True)
    costs = sorted(s.limit for s in sellers)
    q = 0
    while q < min(len(values), len(costs)) and values[q] >= costs[q]:
        q += 1
    return (values[q - 1] + costs[q - 1]) / 2


if __name__ == "__main__":
    rng = random.Random(42)  # fixed seed for reproducibility

    print("1) Wealth exchange (1000 agents, equal start of 100):")
    wealth = wealth_exchange(n_agents=1000, rounds=50_000, rng=rng)
    print(f"   Gini before : 0.000")
    print(f"   Gini after  : {gini(wealth):.3f}")
    print(f"   Max / min   : {max(wealth):.1f} / {min(wealth):.1f}")

    print("\n2) Zero-intelligence double auction:")
    buyers = [Trader(limit=rng.uniform(80, 160)) for _ in range(50)]
    sellers = [Trader(limit=rng.uniform(40, 120)) for _ in range(50)]
    prices = double_auction(buyers, sellers, rounds=2000, rng=rng)
    avg = sum(prices) / len(prices)
    print(f"   Trades executed     : {len(prices)}")
    print(f"   Mean trade price    : {avg:.2f}")
    print(f"   Theoretical price   : {theoretical_equilibrium(buyers, sellers):.2f}")
