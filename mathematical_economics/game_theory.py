"""
Game theory — Nash equilibria of 2x2 games / ゲーム理論

A bimatrix game where each player has two strategies. Payoffs are given as
2x2 matrices for the row player and the column player. We find all
pure-strategy Nash equilibria and the (generically unique) mixed-strategy
equilibrium.
"""

from dataclasses import dataclass


@dataclass
class TwoByTwoGame:
    row: list[list[float]]  # row player's payoffs, row[i][j]
    col: list[list[float]]  # column player's payoffs, col[i][j]

    def pure_nash(self) -> list[tuple[int, int]]:
        """Return all (i, j) pure-strategy Nash equilibria."""
        equilibria = []
        for i in range(2):
            for j in range(2):
                # Row player cannot improve by switching its strategy.
                row_best = self.row[i][j] >= self.row[1 - i][j]
                # Column player cannot improve by switching its strategy.
                col_best = self.col[i][j] >= self.col[i][1 - j]
                if row_best and col_best:
                    equilibria.append((i, j))
        return equilibria

    def mixed_nash(self) -> tuple[float, float] | None:
        """Return (p, q): prob. row plays strategy 0, col plays strategy 0.

        Each player mixes to make the opponent indifferent. Returns None when
        no interior mixed equilibrium exists.
        """
        # Column is indifferent  ->  solves for p (row's mix).
        denom_p = self.col[0][0] - self.col[0][1] - self.col[1][0] + self.col[1][1]
        # Row is indifferent  ->  solves for q (column's mix).
        denom_q = self.row[0][0] - self.row[0][1] - self.row[1][0] + self.row[1][1]
        if denom_p == 0 or denom_q == 0:
            return None
        p = (self.col[1][1] - self.col[1][0]) / denom_p
        q = (self.row[1][1] - self.row[0][1]) / denom_q
        if 0 <= p <= 1 and 0 <= q <= 1:
            return p, q
        return None


if __name__ == "__main__":
    # Prisoner's Dilemma (0 = cooperate, 1 = defect); higher payoff is better.
    pd = TwoByTwoGame(
        row=[[-1, -3], [0, -2]],
        col=[[-1, 0], [-3, -2]],
    )
    print("Prisoner's Dilemma pure Nash:", pd.pure_nash())

    # Matching Pennies — no pure equilibrium, mixed at (0.5, 0.5).
    mp = TwoByTwoGame(
        row=[[1, -1], [-1, 1]],
        col=[[-1, 1], [1, -1]],
    )
    print("Matching Pennies pure Nash:", mp.pure_nash())
    print("Matching Pennies mixed Nash:", mp.mixed_nash())
