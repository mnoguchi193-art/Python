"""
研究シミュレーションの共有コア / A single study: test, power, effect size

心理学の再現性危機を分析するための統計エンジン。2群比較 (効果量 Cohen's d) の
検定・p値・検出力 (power) を、標準正規分布 (math.erf) で計算する。
他モジュールの共有コア。

⚠ 教育目的の簡略モデル。正規近似の z 検定を用い、パラメータは説明用の設定です。
"""

import math
import random

# ── 正規分布 / normal distribution via erf ──────────────────────────────
def phi(x):
    """標準正規分布の累積分布関数 / standard normal CDF"""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2)))

def inv_phi(p):
    """標準正規分布の逆関数 (Acklam の有理近似) / inverse normal CDF"""
    if p <= 0.0:
        return -float("inf")
    if p >= 1.0:
        return float("inf")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)

def z_crit(alpha=0.05):
    """両側検定の臨界値 / two-sided critical value"""
    return inv_phi(1 - alpha / 2)

# ── 検出力 / statistical power ────────────────────────────────────────────
def power(d, n_per_group, alpha=0.05):
    """真の効果量 d・各群 n のとき、有意になる確率 (検出力)"""
    ncp = d * math.sqrt(n_per_group / 2)      # 非心度 / noncentrality
    zc = z_crit(alpha)
    return (1 - phi(zc - ncp)) + phi(-zc - ncp)

# ── 1つの研究をシミュレート / simulate one study ──────────────────────────
def simulate_study(d_true, n_per_group, rng, alpha=0.05):
    """観測効果量・p値・有意かどうかを返す。

    平均差の標本分布 d_hat ~ Normal(d_true, sqrt(2/n)) を直接引く
    (正規モデルでの厳密な標本分布)。"""
    se = math.sqrt(2 / n_per_group)
    d_hat = rng.gauss(d_true, se)
    z = d_hat / se
    p = 2 * (1 - phi(abs(z)))
    return dict(d_hat=d_hat, p=p, significant=(p < alpha), n=n_per_group)

# ── デモ / demo ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("statistical power by sample size and true effect (α=0.05, two-sided):")
    print(f"  {'n/group':>8} | " + " ".join(f"d={d}" for d in (0.2, 0.35, 0.5, 0.8)))
    for n in (15, 25, 40, 64, 100):
        powers = [power(d, n) for d in (0.2, 0.35, 0.5, 0.8)]
        print(f"  {n:>8} | " + "  ".join(f"{p:>4.0%}" for p in powers))

    # 典型的な心理学研究の検出力 / typical psychology study power
    print("\ntypical psychology study: n≈25/group, small-to-medium true effect d≈0.35")
    print(f"  → power ≈ {power(0.35, 25):.0%}  "
          f"(underpowered: even a REAL effect is missed most of the time)")
    print(f"  to reach 80% power for d=0.35, need n ≈ ", end="")
    n = 2
    while power(0.35, n) < 0.80:
        n += 1
    print(f"{n}/group")

    # 検定の妥当性チェック / sanity check via simulation
    rng = random.Random(0)
    N = 20000
    false_pos = sum(simulate_study(0.0, 25, rng)["significant"] for _ in range(N)) / N
    detected = sum(simulate_study(0.35, 25, rng)["significant"] for _ in range(N)) / N
    print(f"\nsimulation check ({N:,} studies):")
    print(f"  false-positive rate at d=0 : {false_pos:.1%} (should ≈ 5%)")
    print(f"  detection rate at d=0.35   : {detected:.1%} (matches power {power(0.35, 25):.0%})")
    print("\n→ 心理学の多くの研究は検出力不足。真の効果すら見逃す一方、")
    print("  有意になった結果は次モジュールで見る『偏り』を抱えやすい")
