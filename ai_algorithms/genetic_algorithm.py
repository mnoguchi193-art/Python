"""
Genetic Algorithm (遺伝的アルゴリズム)

進化の仕組み (選択・交叉・突然変異) を模倣した最適化手法。
ランダムな文字列の集団を目標文字列へと進化させる。
"""

from __future__ import annotations
import random
import string

TARGET = "HELLO GENETIC ALGORITHM"
GENES = string.ascii_uppercase + " "


def fitness(individual: str, target: str = TARGET) -> int:
    """目標と一致する文字数。大きいほど良い。"""
    return sum(a == b for a, b in zip(individual, target))


def tournament_select(population: list[str], rng: random.Random, k: int = 3) -> str:
    """ランダムに k 個体を選び、最良の個体を返す (トーナメント選択)。"""
    return max(rng.sample(population, k), key=fitness)


def crossover(parent_a: str, parent_b: str, rng: random.Random) -> str:
    """一様交叉: 各遺伝子を親のどちらかからランダムに継承する。"""
    return "".join(rng.choice(pair) for pair in zip(parent_a, parent_b))


def mutate(individual: str, rng: random.Random, rate: float = 0.02) -> str:
    """突然変異: 各遺伝子を確率 rate でランダムな遺伝子に置き換える。"""
    return "".join(
        rng.choice(GENES) if rng.random() < rate else gene for gene in individual
    )


def evolve(
    target: str = TARGET,
    population_size: int = 200,
    max_generations: int = 500,
    elite: int = 2,
    seed: int = 42,
) -> tuple[str, int]:
    """Return (best_individual, generations_taken)."""
    rng = random.Random(seed)
    population = [
        "".join(rng.choice(GENES) for _ in target) for _ in range(population_size)
    ]
    for generation in range(max_generations):
        population.sort(key=fitness, reverse=True)
        best = population[0]
        if best == target:
            return best, generation
        # エリート保存 + 選択→交叉→突然変異で次世代を生成
        next_gen = population[:elite]
        while len(next_gen) < population_size:
            child = crossover(
                tournament_select(population, rng),
                tournament_select(population, rng),
                rng,
            )
            next_gen.append(mutate(child, rng))
        population = next_gen
    population.sort(key=fitness, reverse=True)
    return population[0], max_generations


if __name__ == "__main__":
    rng = random.Random(42)
    population = ["".join(rng.choice(GENES) for _ in TARGET) for _ in range(200)]
    print("Initial best:", max(population, key=fitness))

    best, generations = evolve()
    print(f"Evolved best: {best}")
    print(f"Generations:  {generations}")
    print(f"Fitness:      {fitness(best)}/{len(TARGET)}")
