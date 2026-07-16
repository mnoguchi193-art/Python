"""
情報理論の共有コア / Shared information-theory utilities

意識の計算理論 (統合情報理論・グローバルワークスペース等) の解析で使う
エントロピー・相互情報量・ロジスティック関数などの基本道具。

⚠ 教育目的の簡略実装です。
"""

import math

def log2(x):
    return math.log(x, 2) if x > 0 else 0.0

# ── エントロピー / entropy ────────────────────────────────────────────────
def entropy(probs):
    """確率分布 (リストか辞書の値) のシャノンエントロピー (bits)"""
    vals = probs.values() if isinstance(probs, dict) else probs
    return -sum(p * log2(p) for p in vals if p > 0)

def binary_entropy(p):
    """ベルヌーイ分布のエントロピー Hb(p)"""
    return -(p * log2(p) + (1 - p) * log2(1 - p)) if 0 < p < 1 else 0.0

def dist_from_counts(counts):
    """出現回数 → 確率分布"""
    total = sum(counts.values()) if isinstance(counts, dict) else sum(counts)
    if isinstance(counts, dict):
        return {k: v / total for k, v in counts.items()}
    return [v / total for v in counts]

# ── 相互情報量 / mutual information ──────────────────────────────────────
def mutual_information(joint):
    """同時分布 joint[(x,y)] = p(x,y) から I(X;Y) を計算 (bits)"""
    px, py = {}, {}
    for (x, y), p in joint.items():
        px[x] = px.get(x, 0) + p
        py[y] = py.get(y, 0) + p
    mi = 0.0
    for (x, y), p in joint.items():
        if p > 0:
            mi += p * log2(p / (px[x] * py[y]))
    return mi

def kl_divergence(p, q):
    """KL ダイバージェンス D(p||q) — 辞書 (同じキー) 同士"""
    return sum(p[k] * log2(p[k] / q[k]) for k in p if p[k] > 0)

# ── ロジスティック / logistic ─────────────────────────────────────────────
def logistic(x, gain=1.0, bias=0.0):
    return 1.0 / (1.0 + math.exp(-(gain * x + bias)))

# ── 正規分布 / normal distribution (信号検出理論で使う) ──────────────────
def normal_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2)))

def inv_normal(p):
    """標準正規の逆関数 (Acklam 近似)。d' 等の計算に使う"""
    if p <= 0:
        return -6.0
    if p >= 1:
        return 6.0
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
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)

# ── デモ / demo ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("entropy of distributions (bits):")
    for name, d in [("fair coin", [0.5, 0.5]),
                    ("biased 0.9", [0.9, 0.1]),
                    ("certain", [1.0, 0.0]),
                    ("uniform-4", [0.25] * 4)]:
        print(f"  {name:<12} H = {entropy(d):.3f}")

    print("\nmutual information — two coupled bits:")
    # 完全相関 / perfectly correlated
    corr = {(0, 0): 0.5, (1, 1): 0.5}
    indep = {(x, y): 0.25 for x in (0, 1) for y in (0, 1)}
    partial = {(0, 0): 0.4, (0, 1): 0.1, (1, 0): 0.1, (1, 1): 0.4}
    print(f"  perfectly correlated : I = {mutual_information(corr):.3f} bits (= 1, fully shared)")
    print(f"  independent          : I = {mutual_information(indep):.3f} bits (= 0)")
    print(f"  partially coupled    : I = {mutual_information(partial):.3f} bits")
    print("\n→ 統合情報理論はこの『相互情報量』を全体 vs 部分で比べて意識の量 Φ を測る")
