"""
スケーリング則と学習コスト / Scaling laws and training economics

Chinchilla 型のスケーリング則 (簡略版) を使って、モデルサイズ・データ量・
計算量 (FLOPs) と学習コストの関係、収穫逓減を見るデモ。
(係数は説明用の近似値です / coefficients are illustrative approximations)
"""

import math

# ── Chinchilla 型損失関数 / parametric loss L(N, D) ──────────────────────
# L(N, D) = E + A / N^alpha + B / D^beta
#   N: パラメータ数, D: 学習トークン数
E, A, B = 1.69, 406.4, 410.7
ALPHA, BETA = 0.34, 0.28

def loss(n_params: float, n_tokens: float) -> float:
    return E + A / n_params**ALPHA + B / n_tokens**BETA

def train_flops(n_params: float, n_tokens: float) -> float:
    return 6 * n_params * n_tokens  # 経験則: FLOPs ≈ 6ND

# ── 計算予算固定で N と D の最適配分 / compute-optimal allocation ─────────
# Chinchilla の結論: 予算 C に対し N と D をほぼ同率で増やす (D/N ≈ 20)
COST_PER_FLOP = 2.5e-18  # USD/FLOP (GPU レンタル換算, 架空値)

print(f"{'params':>8} {'tokens':>8} {'loss':>7} {'FLOPs':>9} {'cost':>12}")
for n in (1e9, 1e10, 1e11, 1e12):
    d = 20 * n  # compute-optimal な比率
    c = train_flops(n, d)
    print(f"{n:>8.0e} {d:>8.0e} {loss(n, d):>7.3f} {c:>9.2e} ${c * COST_PER_FLOP:>10,.0f}")

# ── 収穫逓減 / diminishing returns ───────────────────────────────────────
# 損失を一定量下げるのに必要なコストが指数的に増えることを確認する
print("\ncost to reach each loss target (compute-optimal):")
targets = [2.2, 2.0, 1.9, 1.85]
for target in targets:
    # L(N, 20N) = target を二分法で解く / bisection on log10(N)
    lo, hi = 6.0, 15.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if loss(10**mid, 20 * 10**mid) > target:
            lo = mid
        else:
            hi = mid
    n = 10**((lo + hi) / 2)
    cost = train_flops(n, 20 * n) * COST_PER_FLOP
    print(f"  loss {target:.2f} → {n:.1e} params, ${cost:,.0f}")

# ── 推論コストとの綱引き / training vs inference trade-off ────────────────
# 小さいモデルを長く学習 (over-training) すると、学習費は増えるが推論費が下がる。
# 総コスト = 学習費 + 推論単価 × 生涯リクエスト数 で比較する。
LIFETIME_TOKENS = 1e13  # 運用期間中に生成する総トークン数
INFER_FLOPS_PER_TOKEN = lambda n: 2 * n  # 経験則: 推論 FLOPs ≈ 2N/token

print(f"\ntotal cost of ownership (serving {LIFETIME_TOKENS:.0e} tokens):")
target_loss = 2.0
for ratio in (20, 100, 500):  # D/N 比を変えて同じ損失を狙う
    lo, hi = 6.0, 15.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if loss(10**mid, ratio * 10**mid) > target_loss:
            lo = mid
        else:
            hi = mid
    n = 10**((lo + hi) / 2)
    train_cost = train_flops(n, ratio * n) * COST_PER_FLOP
    infer_cost = INFER_FLOPS_PER_TOKEN(n) * LIFETIME_TOKENS * COST_PER_FLOP
    print(f"  D/N={ratio:>3}: {n:.1e} params, train ${train_cost:>9,.0f} "
          f"+ infer ${infer_cost:>9,.0f} = ${train_cost + infer_cost:>10,.0f}")
