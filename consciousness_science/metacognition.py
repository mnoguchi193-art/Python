"""
メタ認知と高次の意識理論 / Metacognition and higher-order awareness

信号検出理論で、一次の感度 d' (課題成績) と二次のメタ認知感度 (確信度が
正誤をどれだけ追えるか) を分離して測るデモ。メタ認知ノイズを加えると、
成績 (d') は保ったまま気づき (メタ認知) だけが低下する — 盲視 (blindsight) の
ように『できるが気づいていない』解離を再現する。高次理論の視点。

⚠ 教育目的の簡略モデルです。メタ認知感度は type-2 ROC 曲線下面積で近似する。
"""

import random

from info_theory import inv_normal, normal_cdf

# ── 信号検出の試行をシミュレート / simulate SDT trials ───────────────────
def run_trials(d_prime, meta_noise, n=40000, seed=0):
    """信号あり/なしの証拠を引き、判断と確信度を生成する。

    証拠 e ~ N(±d'/2, 1)。判断は e>0 で『信号あり』。確信度は判断からの
    距離 |e| にメタ認知ノイズを加えたもの (ノイズが大きいほど確信が当てにならない)。
    """
    rng = random.Random(seed)
    trials = []
    for _ in range(n):
        signal = rng.random() < 0.5
        e = rng.gauss(d_prime / 2 if signal else -d_prime / 2, 1.0)
        choice = e > 0
        correct = (choice == signal)
        conf = abs(e) + rng.gauss(0, meta_noise)   # メタ認知ノイズ
        trials.append((signal, choice, correct, conf))
    return trials

# ── 一次感度 d' / type-1 sensitivity ─────────────────────────────────────
def type1_dprime(trials):
    hits = sum(1 for s, c, _, _ in trials if s and c)
    signal = sum(1 for s, _, _, _ in trials if s)
    fas = sum(1 for s, c, _, _ in trials if not s and c)
    noise = sum(1 for s, _, _, _ in trials if not s)
    H = min(max(hits / signal, 1e-4), 1 - 1e-4)
    F = min(max(fas / noise, 1e-4), 1 - 1e-4)
    return inv_normal(H) - inv_normal(F)

# ── 二次感度: type-2 ROC の曲線下面積 / metacognitive sensitivity ────────
def type2_auroc(trials):
    """確信度が正答と誤答をどれだけ区別できるか (0.5=無, 1.0=完全)"""
    confs = sorted(set(round(c, 2) for _, _, _, c in trials))
    correct = [c for _, _, ok, c in trials if ok]
    wrong = [c for _, _, ok, c in trials if not ok]
    nc, nw = len(correct), len(wrong)
    if not nc or not nw:
        return 0.5
    pts = [(0.0, 0.0)]
    for thr in confs:
        tp = sum(1 for c in correct if c >= thr) / nc   # 正答を高確信と当てる率
        fp = sum(1 for c in wrong if c >= thr) / nw     # 誤答を高確信と誤る率
        pts.append((fp, tp))
    pts.append((1.0, 1.0))
    pts.sort()
    area = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        area += (x1 - x0) * (y0 + y1) / 2
    return area

# ── 実行 / run ───────────────────────────────────────────────────────────
print("dissociating performance (d') from awareness (metacognition):")
print(f"  {'condition':<34} {'d-prime':>8} {'meta-AUROC':>11}  awareness")
conditions = [
    ("ideal metacognition",          1.5, 0.0),
    ("mild metacognitive noise",     1.5, 1.0),
    ("strong metacognitive noise",   1.5, 3.0),
    ("blindsight-like (severe)",     1.5, 8.0),
]
for name, d, mn in conditions:
    trials = run_trials(d, mn)
    d1 = type1_dprime(trials)
    auc = type2_auroc(trials)
    aware = ("high" if auc > 0.7 else "reduced" if auc > 0.58 else "near-absent")
    bar = "#" * int((auc - 0.5) * 60)
    print(f"  {name:<34} {d1:>8.2f} {auc:>11.3f}  {aware:<11} {bar}")

print("→ d' (成績) は全条件でほぼ一定なのに、メタ認知ノイズで気づき (AUROC) だけが低下")
print("  → 『見えている性能はあるのに、見えている感覚がない』= 盲視的な解離")

# ── 確信度-正答率の対応 / confidence-accuracy calibration ────────────────
print("\naccuracy by confidence level (ideal vs noisy metacognition):")
for name, d, mn in [("ideal", 1.5, 0.0), ("noisy", 1.5, 4.0)]:
    trials = run_trials(d, mn)
    confs = sorted(c for _, _, _, c in trials)
    lo_cut, hi_cut = confs[len(confs) // 3], confs[2 * len(confs) // 3]
    bins = {"low": [], "mid": [], "high": []}
    for _, _, ok, c in trials:
        b = "low" if c < lo_cut else ("high" if c >= hi_cut else "mid")
        bins[b].append(ok)
    accs = {b: sum(v) / len(v) for b, v in bins.items()}
    print(f"  {name:<7} low-conf {accs['low']:.0%}  mid {accs['mid']:.0%}  "
          f"high-conf {accs['high']:.0%}"
          + ("   (confidence tracks accuracy)" if name == "ideal"
             else "   (confidence barely tracks accuracy)"))

print("""
→ 良いメタ認知では『高確信ほど正答率が高い』— 確信度が自分の正しさを追う
→ メタ認知ノイズが強いと、成績は同じでも確信度が正誤を追えなくなる
→ 高次理論 (higher-order theories) は、この『自分の状態への気づき』こそ
  意識の核心だと考える — 一次の処理性能とは別物として扱う
→ IIT (統合)・GWT (放送) とは異なる、意識のもう一つの捉え方""")
