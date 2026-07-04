"""
Minimax with Alpha-Beta Pruning (ゲーム木探索)

二人零和ゲームの最適戦略を求める探索アルゴリズム。
三目並べ (Tic-Tac-Toe) で、負けない手を選ぶAIを実装する。
"""

from __future__ import annotations
from typing import Optional

Board = list[str]  # 長さ9のリスト。"X", "O", または " "

LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # cols
    (0, 4, 8), (2, 4, 6),             # diagonals
]


def winner(board: Board) -> Optional[str]:
    for a, b, c in LINES:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    return None


def moves(board: Board) -> list[int]:
    return [i for i, cell in enumerate(board) if cell == " "]


def minimax(
    board: Board,
    player: str,
    maximizing: str,
    alpha: float = float("-inf"),
    beta: float = float("inf"),
    depth: int = 0,
) -> int:
    """maximizing 視点のスコアを返す (+10 勝ち / -10 負け / 0 引き分け)。

    depth を加減することで「早い勝ち・遅い負け」を優先する。
    alpha-beta 枝刈りにより探索ノード数を大幅に削減する。
    """
    win = winner(board)
    if win == maximizing:
        return 10 - depth
    if win is not None:
        return depth - 10
    if not moves(board):
        return 0

    opponent = "O" if player == "X" else "X"
    if player == maximizing:
        best = float("-inf")
        for move in moves(board):
            board[move] = player
            best = max(best, minimax(board, opponent, maximizing, alpha, beta, depth + 1))
            board[move] = " "
            alpha = max(alpha, best)
            if beta <= alpha:
                break  # β刈り
        return int(best)
    else:
        best = float("inf")
        for move in moves(board):
            board[move] = player
            best = min(best, minimax(board, opponent, maximizing, alpha, beta, depth + 1))
            board[move] = " "
            beta = min(beta, best)
            if beta <= alpha:
                break  # α刈り
        return int(best)


def best_move(board: Board, player: str) -> int:
    opponent = "O" if player == "X" else "X"
    return max(
        moves(board),
        key=lambda m: _score_move(board, m, player, opponent),
    )


def _score_move(board: Board, move: int, player: str, opponent: str) -> int:
    board[move] = player
    score = minimax(board, opponent, maximizing=player)
    board[move] = " "
    return score


def render(board: Board) -> str:
    rows = [" | ".join(board[i:i + 3]) for i in (0, 3, 6)]
    return "\n---------\n".join(rows)


if __name__ == "__main__":
    # AI (X) 同士の自己対戦: 双方最適なら必ず引き分けになる
    board: Board = [" "] * 9
    player = "X"
    while winner(board) is None and moves(board):
        board[best_move(board, player)] = player
        player = "O" if player == "X" else "X"
    print("Self-play result (both optimal):")
    print(render(board))
    print("Winner:", winner(board) or "draw")

    # 詰みの検出: X は 2 (右上) で即勝ちできる
    board = list("XX OO     ")[:9]
    m = best_move(board, "X")
    print(f"\nTactic test: X to move on\n{render(board)}\n-> best move = {m} (expected 2)")
