"""
再現性: 陽性的中率と再現プロジェクト / Replication: PPV and a replication project

「有意な発見が本当である確率 (陽性的中率 PPV)」を Ioannidis の枠組みで計算し、
現実の文献を模した再現プロジェクトをシミュレートして、なぜ多くの心理現象が
追試で再現しないのか、どの改善策が効くのかを示すデモ。

⚠ 教育目的の簡略モデル。パラメータは説明用の設定です。
   参考: Ioannidis 2005 / Open Science Collaboration 2015 (再現率 ≈ 36%)。
"""

import random

from study import power

# ── 陽性的中率 / positive predictive value (Ioannidis) ───────────────────
# R = 事前オッズ (検証する仮説の 真:偽 の比)。bias u = p ハッキング等の余地。
def ppv(R, pwr, alpha=0.05, bias=0.0):
    tp = pwr + bias * (1 - pwr)            # 真を有意と判定 (バイアス込み)
    fp = alpha + bias * (1 - alpha)        # 偽を有意と判定 (バイアス込み)
    return (tp * R) / (tp * R + fp) if (tp * R + fp) > 0 else 0.0

print("PPV — probability a significant finding is TRUE:")
print(f"  {'prior odds R':>13} | " + " ".join(f"pwr={p:.0%}" for p in (0.2, 0.5, 0.8)))
for R, label in [(1 / 5, "1:5 (novel)"), (1 / 2, "1:2"), (1 / 1, "1:1"), (2 / 1, "2:1 (safe)")]:
    ppvs = [ppv(R, p) for p in (0.2, 0.5, 0.8)]
    print(f"  {label:>13} | " + "   ".join(f"{v:>4.0%}" for v in ppvs))
print("  with p-hacking bias u=0.3 (R=1:2, power=0.2):")
print(f"    PPV drops to {ppv(1/2, 0.2, bias=0.3):.0%}  (most 'findings' are false)")
print("→ 検出力が低く・新奇 (R小) で・バイアスがあるほど、有意でも偽の確率が高い")

# ── 再現プロジェクトのシミュレーション / replication-project simulation ──
# 追試は常に高検出力で実施する (α=0.05, d_true で約90%)。改善策は『出版される
# 文献の質 (PPV)』だけを変え、追試の検出性は一定に保つ — 再現率は PPV に単調に効く。
N_REP, ALPHA_REP = 110, 0.05

def run_literature(base_rate, n_orig, d_true=0.4, alpha_pub=0.05,
                   phack=False, seed=0, n_candidates=40000):
    """多数の候補研究から『出版された発見』を作り、直接追試して再現率を測る"""
    rng = random.Random(seed)
    pub, replicated = 0, 0
    pwr_orig = power(d_true, n_orig, alpha_pub)
    false_pub = (0.30 if phack else alpha_pub)              # 偽仮説が出版される率
    true_pub = min(1.0, pwr_orig + (0.25 if phack else 0))  # 真仮説が出版される率
    pwr_rep = power(d_true, N_REP, ALPHA_REP)               # 追試の検出力 (一定)
    for _ in range(n_candidates):
        is_true = rng.random() < base_rate
        published = rng.random() < (true_pub if is_true else false_pub)
        if not published:
            continue
        pub += 1
        threshold = pwr_rep if is_true else ALPHA_REP / 2   # 偽陽性が同方向で再現する稀確率
        if rng.random() < threshold:
            replicated += 1
    return replicated / pub if pub else 0.0, pub

print(f"\nreplication rate of the published literature "
      f"(replications fixed at ~{power(0.4, N_REP):.0%} power):")
print(f"  {'regime (each fix added cumulatively)':<40} {'replication rate':>16}")
regimes = [
    ("current practice (low power, p-hacking)",
     dict(base_rate=0.3, n_orig=25, phack=True, alpha_pub=0.05)),
    ("+ preregistration (no p-hacking)",
     dict(base_rate=0.3, n_orig=25, phack=False, alpha_pub=0.05)),
    ("+ high power (n=100 originals)",
     dict(base_rate=0.3, n_orig=100, phack=False, alpha_pub=0.05)),
    ("+ stricter threshold (α=0.005)",
     dict(base_rate=0.3, n_orig=100, phack=False, alpha_pub=0.005)),
    ("+ test likelier hypotheses (R=1:1)",
     dict(base_rate=0.5, n_orig=100, phack=False, alpha_pub=0.005)),
]
for name, kw in regimes:
    rate, npub = run_literature(**kw, seed=1)
    bar = "#" * int(rate * 40)
    print(f"  {name:<40} {rate:>15.0%}  {bar}")

print("""
→ 「現行実務」の再現率は 4 割前後 — 実際の再現プロジェクト (OSC 2015 ≈ 36%) に近い
→ 前登録・高検出力・厳しいα・有望な仮説の検証を積み重ねると再現率は大きく改善する
→ 単一の魔法の解はない。再現性は『研究の設計・実施・出版』の総体で決まる

新しい心理現象は再現できるのか?
  → 現行の慣行のままでは、多くは再現しない。だが原因は人間心理の気まぐれ以前に、
    低検出力・出版バイアス・研究者の自由度という『方法の問題』にある。
  → これらは設計で修正可能 — 再現性は宿命ではなく、選べる帰結である。""")
