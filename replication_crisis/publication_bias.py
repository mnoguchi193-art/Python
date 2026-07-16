"""
出版バイアスと勝者の呪い / Publication bias and the winner's curse

有意な結果 (p<0.05) だけが出版されると、出版された効果量は真の値より
系統的に大きくなる (勝者の呪い)。とくに検出力が低いほど誇張が激しいことを
シミュレーションと ASCII ファンネルプロットで示すデモ。

⚠ 教育目的の簡略モデル。
"""

import random

from study import power, simulate_study

rng = random.Random(3)

# ── 出版フィルタによる効果量の誇張 / inflation from the publication filter ─
print("published vs true effect size (only p<0.05 gets published):")
print(f"  {'true d':>7} {'n/grp':>6} {'power':>6} {'published d':>12} {'inflation':>10}")
for d_true, n in [(0.3, 20), (0.3, 50), (0.3, 100), (0.5, 20), (0.5, 50), (0.0, 30)]:
    published = []
    for _ in range(30000):
        s = simulate_study(d_true, n, rng)
        if s["significant"]:
            published.append(abs(s["d_hat"]))
    mean_pub = sum(published) / len(published)
    infl = mean_pub / d_true if d_true > 0 else float("inf")
    infl_str = f"x{infl:.2f}" if d_true > 0 else "(false pos!)"
    print(f"  {d_true:>7.1f} {n:>6} {power(d_true, n):>5.0%} {mean_pub:>12.2f} {infl_str:>10}")
print("→ 検出力が低いほど、出版される効果量は真の値を大きく上回る (勝者の呪い)")

# ── ファンネルプロット / funnel plot (effect vs precision) ────────────────
# 真の効果 d=0.3。全研究と『出版された研究』を、精度 (n) 別に配置する。
print("\nfunnel plot — true d=0.30, dashed line = truth")
print("(x = published study; small-n studies survive only if d_hat is large → asymmetry)")
D_TRUE = 0.30
ns = [15, 25, 40, 70, 120]
width = 46
lo, hi = -0.2, 1.0
def col(d):
    return max(0, min(width - 1, int((d - lo) / (hi - lo) * width)))
truth_col = col(D_TRUE)
for n in reversed(ns):
    row = [" "] * width
    row[truth_col] = "|"
    pubs = []
    for _ in range(400):
        s = simulate_study(D_TRUE, n, rng)
        if s["significant"]:
            pubs.append(s["d_hat"])
    for d in pubs[:60]:
        c = col(d)
        row[c] = "x" if row[c] in " |" else "X"
    print(f"  n={n:>3} |" + "".join(row))
print(f"        " + " " * (truth_col) + "^ true effect (0.30)")
print(f"        d: {lo}" + " " * (width - 8) + f"{hi}")

# ── メタ分析での補正 / meta-analysis is also biased if inputs are ────────
# 出版された効果だけを平均すると、メタ分析でも真の値を過大評価する
D_TRUE = 0.30
all_studies, pub_studies = [], []
for _ in range(5000):
    s = simulate_study(D_TRUE, 25, rng)
    all_studies.append(s["d_hat"])
    if s["significant"]:
        pub_studies.append(s["d_hat"])
print(f"\nmeta-analysis of d (true=0.30, n=25/group):")
print(f"  average of ALL studies (incl. unpublished): {sum(all_studies)/len(all_studies):.2f} "
      f"(unbiased)")
print(f"  average of PUBLISHED studies only         : {sum(pub_studies)/len(pub_studies):.2f} "
      f"(inflated)")
print("""
→ 出版バイアスは個々の研究だけでなくメタ分析まで汚染する
→ ファイルドロワー (お蔵入りした非有意研究) を無視すると文献全体が過大評価に傾く
→ だから『有意だった』新奇な心理現象ほど、追試で縮む・消えるリスクが高い""")
