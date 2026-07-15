"""
HANK の家計ブロック / The household block of a HANK model

所得リスク (雇用/失業のマルコフ連鎖) と借入制約に直面する家計の
消費・貯蓄問題を EGM (endogenous grid method) で解くデモ。
限界消費性向 (MPC) が資産水準で大きく異なる — これが HANK と
代表的個人モデル (RANK) を分ける核心。
(パラメータは説明用の架空値です / parameters are illustrative)
"""

import bisect

# ── パラメータ / parameters ──────────────────────────────────────────────
BETA = 0.965            # 割引因子 (β(1+r) < 1 で定常分布が存在)
R = 0.02                # 実質金利
Y = [0.3, 1.0, 3.0]     # 所得: [失業給付, 賃金, 高所得]
P = [[0.50, 0.50, 0.00],  # 失業 → [失業, 就業, 高所得] の遷移確率
     [0.04, 0.93, 0.03],  # 就業 →
     [0.00, 0.20, 0.80]]  # 高所得 →
N_GRID, A_MAX = 120, 50.0
# 借入制約 a >= 0。制約付近の挙動が大事なので 0 近傍を密にする
A_GRID = [A_MAX * (i / (N_GRID - 1)) ** 2 for i in range(N_GRID)]

def interp(xs: list[float], ys: list[float], x: float) -> float:
    """単調な xs 上の線形補間 (範囲外は端の傾きで外挿)"""
    if x <= xs[0]:
        return ys[0]
    i = min(bisect.bisect_right(xs, x), len(xs) - 1) - 1
    t = (x - xs[i]) / (xs[i + 1] - xs[i])
    return ys[i] + t * (ys[i + 1] - ys[i])

# ── EGM で消費政策関数を解く / solve c(a, s) by EGM ───────────────────────
# オイラー方程式 u'(c) = β(1+r) E[u'(c')] を、来期資産グリッドから
# 「今期の資産を逆算」することで、根探索なしで解く (Carroll 2006)。
def solve_policy(r: float = R, y: list[float] | None = None,
                 beta: float = BETA, tol: float = 1e-8) -> list[list[float]]:
    y = y or Y
    n_s = len(y)
    c = [[(1 + r) * a + y[s] for a in A_GRID] for s in range(n_s)]
    for _ in range(3000):
        new_c = []
        for s in range(n_s):
            a_end, c_end = [], []
            for j, a_next in enumerate(A_GRID):
                emu = sum(P[s][sp] / c[sp][j] for sp in range(n_s))  # u'(c)=1/c
                ce = 1.0 / (beta * (1 + r) * emu)
                a_end.append((ce + a_next - y[s]) / (1 + r))
                c_end.append(ce)
            # 制約が締まる領域 (a < a_end[0]) では a'=0 → 全部消費
            new_c.append([
                (1 + r) * a + y[s] if a <= a_end[0] else interp(a_end, c_end, a)
                for a in A_GRID
            ])
        diff = max(abs(new_c[s][i] - c[s][i]) for s in range(n_s) for i in range(N_GRID))
        c = new_c
        if diff < tol:
            break
    return c

def consumption(policy: list[list[float]], s: int, a: float) -> float:
    return interp(A_GRID, policy[s], a)

def mpc(policy: list[list[float]], s: int, a: float, delta: float = 0.01) -> float:
    """臨時収入 δ に対する限界消費性向"""
    return (consumption(policy, s, a + delta) - consumption(policy, s, a)) / delta

# ── 定常分布のシミュレーション / simulate the cross-section ────────────────
def simulate(policy: list[list[float]], n: int = 2000, periods: int = 400,
             r: float = R, seed: int = 42) -> list[tuple[float, int]]:
    import random
    rng = random.Random(seed)
    hh = [[1.0, 1] for _ in range(n)]  # (assets, income state)
    for _ in range(periods):
        for h in hh:
            a, s = h
            a_next = (1 + r) * a + Y[s] - consumption(policy, s, a)
            h[0] = max(a_next, 0.0)
            u, acc = rng.random(), 0.0
            for sp, prob in enumerate(P[s]):
                acc += prob
                if u < acc:
                    h[1] = sp
                    break
    return [(h[0], h[1]) for h in hh]

# ── デモ / demo ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    policy = solve_policy()
    print("consumption policy c(a, s) and MPC:")
    print(f"{'assets':>7} | {'unemp c':>8} {'MPC':>5} | {'emp c':>7} {'MPC':>5} | {'high c':>7} {'MPC':>5}")
    for a in (0.0, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 40.0):
        cells = [f"{consumption(policy, s, a):>7.3f} {mpc(policy, s, a):>5.2f}" for s in range(3)]
        print(f"{a:>7.1f} | {cells[0]:>14} | {cells[1]} | {cells[2]}")
    print("\n→ 借入制約近くの家計は MPC ≈ 1、富裕層は MPC ≈ 0.04")
    print("→ RANK の代表的個人 (MPC ≈ r ≈ 0.02-0.04) では前者が存在しない")
