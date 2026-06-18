"""
Game Theory — Nash equilibria of normal-form games

The foundation of modern microeconomics: rational players choosing strategies,
each best-responding to the others. This module finds pure-strategy Nash
equilibria of any 2-player game and the mixed-strategy equilibrium of 2x2 games.

A game is two payoff matrices:
  row[i][j] = payoff to the ROW player when row plays i, column plays j
  col[i][j] = payoff to the COLUMN player for the same outcome
"""

from __future__ import annotations

Matrix = list[list[float]]


def pure_nash(row: Matrix, col: Matrix) -> list[tuple[int, int]]:
    """All pure-strategy Nash equilibria as (row_action, col_action) pairs."""
    n_rows, n_cols = len(row), len(row[0])
    equilibria = []
    for i in range(n_rows):
        for j in range(n_cols):
            row_best = row[i][j] == max(row[k][j] for k in range(n_rows))
            col_best = col[i][j] == max(col[i][k] for k in range(n_cols))
            if row_best and col_best:
                equilibria.append((i, j))
    return equilibria


def mixed_nash_2x2(row: Matrix, col: Matrix) -> tuple[float, float] | None:
    """Interior mixed equilibrium of a 2x2 game.

    Returns (p, q) where p = P(row plays action 0), q = P(col plays action 0),
    each player mixing so the *other* is indifferent. None if no interior
    solution exists (e.g. a dominant strategy).
    """
    # Column is indifferent between its actions => solve for p.
    denom_p = (col[0][0] - col[1][0]) - (col[0][1] - col[1][1])
    # Row is indifferent between its actions => solve for q.
    denom_q = (row[0][0] - row[0][1]) - (row[1][0] - row[1][1])
    if denom_p == 0 or denom_q == 0:
        return None
    p = (col[1][1] - col[1][0]) / denom_p
    q = (row[1][1] - row[0][1]) / denom_q
    if 0 <= p <= 1 and 0 <= q <= 1:
        return p, q
    return None


if __name__ == "__main__":
    # Prisoner's Dilemma (0=Cooperate, 1=Defect). Lower jail time is better,
    # so payoffs are negative years.
    pd_row = [[-1, -3], [0, -2]]
    pd_col = [[-1, 0], [-3, -2]]
    print("Prisoner's Dilemma")
    print(f"  Pure Nash: {pure_nash(pd_row, pd_col)}  -> both Defect (1, 1)")
    print(f"  Mixed Nash: {mixed_nash_2x2(pd_row, pd_col)}  (dominant strategy)\n")

    # Matching Pennies — a zero-sum game with NO pure equilibrium.
    mp_row = [[1, -1], [-1, 1]]
    mp_col = [[-1, 1], [1, -1]]
    print("Matching Pennies")
    print(f"  Pure Nash: {pure_nash(mp_row, mp_col)}  (none exists)")
    print(f"  Mixed Nash (p, q): {mixed_nash_2x2(mp_row, mp_col)}  -> both 50/50\n")

    # Battle of the Sexes — two pure equilibria plus a mixed one.
    bs_row = [[2, 0], [0, 1]]
    bs_col = [[1, 0], [0, 2]]
    print("Battle of the Sexes")
    print(f"  Pure Nash: {pure_nash(bs_row, bs_col)}")
    print(f"  Mixed Nash (p, q): {mixed_nash_2x2(bs_row, bs_col)}")
