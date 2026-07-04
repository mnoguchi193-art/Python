"""
Genetic Algorithm (遺伝的アルゴリズム / 進化計算)

生物の進化 (選択・交叉・突然変異) を模倣した最適化アルゴリズム。
明示的にプログラムしていない解を「進化」によって発見する。

1. 集団 (population) をランダムに生成
2. 適応度 (fitness) を評価
3. 適応度の高い個体を選択 (トーナメント選択)
4. 交叉 (crossover) で子を作り、突然変異 (mutation) を加える
5. 世代を繰り返す

デモでは目標文字列をランダムな文字列から進化させる。
"""

from __future__ import annotations

import random
import string
from typing import List

GENES = string.ascii_letters + string.digits + " !"


def random_individual(length: int, rng: random.Random) -> str:
    return "".join(rng.choice(GENES) for _ in range(length))


def fitness(individual: str, target: str) -> int:
    """目標文字列と一致する文字数。大きいほど良い。"""
    return sum(a == b for a, b in zip(individual, target))


def tournament_select(population: List[str], target: str,
                      rng: random.Random, k: int = 3) -> str:
    """ランダムに k 個体を選び、最も適応度の高いものを残す。"""
    candidates = rng.sample(population, k)
    return max(candidates, key=lambda ind: fitness(ind, target))


def crossover(parent1: str, parent2: str, rng: random.Random) -> str:
    """一点交叉: 切断点より前を親1、後を親2から受け継ぐ。"""
    point = rng.randint(1, len(parent1) - 1)
    return parent1[:point] + parent2[point:]


def mutate(individual: str, rng: random.Random, rate: float = 0.02) -> str:
    return "".join(
        rng.choice(GENES) if rng.random() < rate else ch for ch in individual
    )


def evolve(target: str, population_size: int = 200,
           max_generations: int = 1000, seed: int = 42) -> str:
    rng = random.Random(seed)
    population = [random_individual(len(target), rng) for _ in range(population_size)]

    for generation in range(max_generations):
        best = max(population, key=lambda ind: fitness(ind, target))
        if generation % 20 == 0 or best == target:
            score = fitness(best, target)
            print(f"gen {generation:4d}  best = {best!r}  ({score}/{len(target)})")
        if best == target:
            print(f"\n{generation} 世代で目標に到達!")
            return best
        # エリート保存: 最良個体はそのまま次世代へ
        next_generation = [best]
        while len(next_generation) < population_size:
            parent1 = tournament_select(population, target, rng)
            parent2 = tournament_select(population, target, rng)
            child = mutate(crossover(parent1, parent2, rng), rng)
            next_generation.append(child)
        population = next_generation

    return max(population, key=lambda ind: fitness(ind, target))


if __name__ == "__main__":
    print("=== 遺伝的アルゴリズムで文字列を進化させる ===\n")
    evolve("Hello AGI World!")
