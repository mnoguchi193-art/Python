"""
定常的な富の分布 / The stationary wealth distribution

家計ブロックの政策関数で多数の家計をシミュレートし、HANK の土台となる
「富の不平等」と hand-to-mouth 家計の割合を見るデモ。
(パラメータは説明用の架空値です / parameters are illustrative)
"""

from household import Y, solve_policy, simulate

policy = solve_policy()
cross_section = simulate(policy, n=3000, periods=500)
assets = sorted(a for a, _ in cross_section)
n = len(assets)
total = sum(assets)

# ── 基本統計 / summary statistics ────────────────────────────────────────
mean = total / n
median = assets[n // 2]
print(f"households: {n:,}, mean wealth: {mean:.2f}, median: {median:.2f}")
print(f"mean/median ratio: {mean / median:.2f} (right-skewed distribution)")

# ── ジニ係数 / Gini coefficient ──────────────────────────────────────────
gini = 2 * sum((i + 1) * a for i, a in enumerate(assets)) / (n * total) - (n + 1) / n
print(f"wealth Gini: {gini:.3f}")

# ── 富の集中 / concentration ─────────────────────────────────────────────
def top_share(fraction: float) -> float:
    k = int(n * fraction)
    return sum(assets[n - k:]) / total

print(f"top 10% hold {top_share(0.10):.0%}, top 1% hold {top_share(0.01):.0%}, "
      f"bottom 50% hold {sum(assets[:n // 2]) / total:.0%}")

# ── hand-to-mouth 家計 / hand-to-mouth households ────────────────────────
# 資産が月収程度以下しかなく、所得ショックを平準化できない家計。
# HANK の集計的な反応 (高い平均MPC) を駆動するのはこの層。
HTM_CUTOFF = Y[1] / 12  # 月収相当
htm = sum(1 for a, _ in cross_section if a <= HTM_CUTOFF) / n
unemployed = sum(1 for _, s in cross_section if s == 0) / n
print(f"\nhand-to-mouth share (a <= 1 month income): {htm:.0%}")
print(f"unemployment rate in cross-section: {unemployed:.0%}")
print("(実証では HtM は約3割 — 1資産モデルは過小評価し、2資産 HANK が埋める)")

# ── 分布のヒストグラム / ASCII histogram ─────────────────────────────────
print("\nwealth distribution:")
BINS = [(0, 0.5), (0.5, 1), (1, 2), (2, 4), (4, 8), (8, 16), (16, 999)]
for lo, hi in BINS:
    count = sum(1 for a in assets if lo <= a < hi)
    label = f"{lo:>4.1f}-{hi:<4.1f}" if hi < 999 else f"{lo:>4.1f}+   "
    print(f"  {label} {'#' * (count * 120 // n):<40} {count / n:.0%}")

print("\n→ 同質な家計でも、所得リスク×借入制約だけで富の不平等が内生的に生まれる")
print("→ 平均的な家計は存在しない — 分布全体がマクロの反応を決める (HANKの出発点)")
