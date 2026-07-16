"""
反応速度論の共有コア / Shared kinetics utilities

生命の起源の各モデルで使う数値積分 (RK4) と、自己複製の基本である
自己触媒反応 (ロジスティック成長) のデモ。他モジュールの共有コア。

⚠ 教育目的の簡略モデルです。
"""

# ── 汎用 RK4 積分器 / generic RK4 integrator ──────────────────────────────
def rk4_step(deriv, state, t, dt):
    k1 = deriv(state, t)
    k2 = deriv([s + 0.5 * dt * a for s, a in zip(state, k1)], t + 0.5 * dt)
    k3 = deriv([s + 0.5 * dt * a for s, a in zip(state, k2)], t + 0.5 * dt)
    k4 = deriv([s + dt * a for s, a in zip(state, k3)], t + dt)
    return [s + dt / 6 * (a + 2 * b + 2 * c + d)
            for s, a, b, c, d in zip(state, k1, k2, k3, k4)]

def integrate(deriv, state0, t0, t1, dt, clamp_nonneg=True):
    ts, ys = [t0], [list(state0)]
    state, t = list(state0), t0
    for _ in range(round((t1 - t0) / dt)):
        state = rk4_step(deriv, state, t, dt)
        if clamp_nonneg:
            state = [max(x, 0.0) for x in state]
        t += dt
        ts.append(t)
        ys.append(state)
    return ts, ys

# ── デモ: 自己触媒反応 = 自己複製の芽 / autocatalysis → self-replication ──
if __name__ == "__main__":
    # A + X → 2X : 資源 A を使って X が自分のコピーを作る (最も単純な複製)
    # dX/dt = k·X·(1 − X/K)  — 資源枯渇で頭打ちになるロジスティック成長
    K, k = 1.0, 0.8

    def deriv(state, t):
        x = state[0]
        return [k * x * (1 - x / K)]

    ts, ys = integrate(deriv, [0.01], 0, 20, 0.1)
    print("autocatalytic growth A + X → 2X (the seed of self-replication):")
    print("  time  X (replicator concentration)")
    for i in range(0, len(ts), 20):
        x = ys[i][0]
        print(f"  {ts[i]:>4.0f}  {x:>5.3f}  {'#' * int(x * 40)}")
    print("\n→ 自分の生成を触媒する分子は指数的に増える — これが『複製』の物理的な芽")
    print("→ 生命の起源とは、こうした自己触媒がどう生じ・情報を運び・区画化されたかの問い")
    print("  (自己触媒集合・複製の忠実度・原始細胞・ホモキラリティ — 各モジュール参照)")
