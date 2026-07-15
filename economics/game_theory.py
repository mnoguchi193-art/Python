"""
Game Theory (ゲーム理論)

Two-player normal-form games: pure-strategy Nash equilibria, dominant
strategies, and an iterated prisoner's dilemma tournament in the spirit
of Axelrod's experiments.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

# A payoff matrix maps (row_action, col_action) -> (row_payoff, col_payoff)
Payoffs = dict[tuple[str, str], tuple[float, float]]

PRISONERS_DILEMMA: Payoffs = {
    ("cooperate", "cooperate"): (3, 3),
    ("cooperate", "defect"):    (0, 5),
    ("defect", "cooperate"):    (5, 0),
    ("defect", "defect"):       (1, 1),
}


@dataclass
class NormalFormGame:
    payoffs: Payoffs

    @property
    def row_actions(self) -> list[str]:
        return sorted({r for r, _ in self.payoffs})

    @property
    def col_actions(self) -> list[str]:
        return sorted({c for _, c in self.payoffs})

    def best_responses(self, player: int, opponent_action: str) -> set[str]:
        """Actions maximizing `player`'s payoff against a fixed opponent action."""
        if player == 0:
            options = {a: self.payoffs[(a, opponent_action)][0] for a in self.row_actions}
        else:
            options = {a: self.payoffs[(opponent_action, a)][1] for a in self.col_actions}
        best = max(options.values())
        return {a for a, v in options.items() if v == best}

    def nash_equilibria(self) -> list[tuple[str, str]]:
        """All pure-strategy Nash equilibria (mutual best responses)."""
        return [
            (r, c)
            for r in self.row_actions
            for c in self.col_actions
            if r in self.best_responses(0, c) and c in self.best_responses(1, r)
        ]

    def dominant_strategy(self, player: int) -> str | None:
        """A strategy that is a best response to every opponent action."""
        own = self.row_actions if player == 0 else self.col_actions
        opp = self.col_actions if player == 0 else self.row_actions
        for action in own:
            if all(action in self.best_responses(player, o) for o in opp):
                return action
        return None


# --- Iterated prisoner's dilemma ------------------------------------------
# A strategy sees (my_history, opponent_history) and returns an action.
Strategy = Callable[[list[str], list[str]], str]


def always_cooperate(mine: list[str], theirs: list[str]) -> str:
    return "cooperate"


def always_defect(mine: list[str], theirs: list[str]) -> str:
    return "defect"


def tit_for_tat(mine: list[str], theirs: list[str]) -> str:
    return theirs[-1] if theirs else "cooperate"


def grudger(mine: list[str], theirs: list[str]) -> str:
    return "defect" if "defect" in theirs else "cooperate"


def play_iterated(s1: Strategy, s2: Strategy, rounds: int,
                  payoffs: Payoffs = PRISONERS_DILEMMA) -> tuple[float, float]:
    """Total payoffs for both strategies over `rounds` repetitions."""
    h1: list[str] = []
    h2: list[str] = []
    score1 = score2 = 0.0
    for _ in range(rounds):
        a1, a2 = s1(h1, h2), s2(h2, h1)
        p1, p2 = payoffs[(a1, a2)]
        score1, score2 = score1 + p1, score2 + p2
        h1.append(a1)
        h2.append(a2)
    return score1, score2


def tournament(strategies: dict[str, Strategy], rounds: int = 100) -> dict[str, float]:
    """Round-robin: every strategy plays every other (and itself) once."""
    totals = {name: 0.0 for name in strategies}
    names = list(strategies)
    for i, n1 in enumerate(names):
        for n2 in names[i:]:
            s1, s2 = play_iterated(strategies[n1], strategies[n2], rounds)
            totals[n1] += s1
            if n1 != n2:
                totals[n2] += s2
    return totals


if __name__ == "__main__":
    game = NormalFormGame(PRISONERS_DILEMMA)
    print("Prisoner's dilemma")
    print(f"  Nash equilibria    : {game.nash_equilibria()}")
    print(f"  Dominant (player 0): {game.dominant_strategy(0)}")

    entrants = {
        "always_cooperate": always_cooperate,
        "always_defect": always_defect,
        "tit_for_tat": tit_for_tat,
        "grudger": grudger,
    }
    print("\nIterated tournament (100 rounds, round-robin):")
    results = tournament(entrants)
    for name, score in sorted(results.items(), key=lambda kv: -kv[1]):
        print(f"  {name:<17}: {score:.0f}")
