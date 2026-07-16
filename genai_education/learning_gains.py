"""
学習成果への影響 / Learning gains: does genAI widen or narrow the gap?

生成AIには「遅れている生徒ほど個別指導の恩恵が大きい」補償的な潜在力がある
(Bloom の 2 シグマ問題)。しかし実際に得られる学習ゲインは『アクセス × 利用の質』
で決まり、これらは高SES層に偏る。放任すると潜在力が逆転して格差を広げることを、
シナリオ比較で示すデモ。

⚠ 教育目的の簡略モデル。パラメータは説明用の架空値です。
"""

from access_model import (access_prob, generate_students, quartile_gap,
                          correlation, use_quality)

# ── 学習ゲインのモデル / learning-gain model ─────────────────────────────
EFFECT = 1.2   # genAI の最大効果量 (標準偏差スケール) / peak effect size

def potential_gain(prior):
    """補償的な潜在力: 事前学力が低いほど伸びしろが大きい (個別指導の効果)"""
    return EFFECT * logistic_room(prior)

def logistic_room(prior):
    # prior が低いほど 1 に近く、高いほど小さい (天井効果)
    import math
    return 1.0 / (1.0 + math.exp(1.1 * prior))

def realized_gain(s, access, quality):
    """実際のゲイン = 潜在力 × アクセス × 利用の質"""
    return potential_gain(s["prior"]) * access * quality

# ── シナリオ / scenarios ─────────────────────────────────────────────────
def run_scenario(students, universal_access=False, quality_support=0.0,
                 target_support_low=False):
    """各シナリオで genAI 導入後の学力を計算して返す"""
    out = []
    for s in students:
        access = 1.0 if universal_access else access_prob(s)
        # 指導支援は利用の質を底上げ。target_support_low なら低SES層に手厚く。
        support = quality_support
        if target_support_low and s["ses"] < 0:
            support = quality_support * 2.0
        quality = use_quality(s, teacher_support=support)
        new = dict(s)
        new["achievement"] = s["prior"] + realized_gain(s, access, quality)
        out.append(new)
    return out

students = generate_students()

# 導入前の基準 / baseline (pre-genAI): achievement = prior
base = [dict(s, achievement=s["prior"]) for s in students]
_, _, base_gap = quartile_gap(base, "achievement")
base_corr = correlation(base, "ses", "achievement")

scenarios = [
    ("baseline (no genAI)",              None),
    ("laissez-faire (unequal access)",   dict()),
    ("universal access only",            dict(universal_access=True)),
    ("universal access + quality support", dict(universal_access=True, quality_support=1.0)),
    ("access + targeted support (low SES)", dict(universal_access=True, quality_support=1.0,
                                               target_support_low=True)),
]

print("SES achievement gap (top vs bottom quartile) under each scenario:")
print(f"  {'scenario':<40} {'gap':>6} {'vs base':>8} {'SES-corr':>9}")
print(f"  {'baseline (no genAI)':<40} {base_gap:>6.2f} {'—':>8} {base_corr:>9.2f}")
for name, kw in scenarios[1:]:
    res = run_scenario(students, **kw)
    _, _, gap = quartile_gap(res, "achievement")
    corr = correlation(res, "ses", "achievement")
    delta = gap - base_gap
    arrow = "widens" if delta > 0.02 else ("narrows" if delta < -0.02 else "~same")
    print(f"  {name:<40} {gap:>6.2f} {delta:>+7.2f}  {corr:>8.2f}  ({arrow})")

# ── 誰がどれだけ伸びたか / gains by SES quartile ─────────────────────────
print("\nmean learning gain by SES quartile:")
print(f"  {'scenario':<40} {'Q1':>6} {'Q2':>6} {'Q3':>6} {'Q4':>6}")
for name, kw in [("laissez-faire", dict()),
                 ("universal access", dict(universal_access=True)),
                 ("access + targeted support", dict(universal_access=True,
                  quality_support=1.0, target_support_low=True))]:
    res = run_scenario(students, **kw)
    ranked = sorted(range(len(students)), key=lambda i: students[i]["ses"])
    q = len(students) // 4
    gains = []
    for k in range(4):
        idx = ranked[k * q:(k + 1) * q]
        g = sum(res[i]["achievement"] - students[i]["prior"] for i in idx) / len(idx)
        gains.append(g)
    print(f"  {name:<40} " + " ".join(f"{g:>6.2f}" for g in gains))

print("""
→ genAI は本来「遅れた生徒ほど伸びる」補償的な潜在力を持つ (低SES層の潜在ゲイン大)
→ ところが放任 (laissez-faire) では、アクセスと利用の質が高SES層に偏るため
  潜在力が逆転し、格差 (SES-学力相関) はむしろ拡大する
→ 全員アクセスだけでは不十分 — 利用の質を底上げして初めて格差が縮む。
  低SES層に的を絞った指導支援が最も格差を縮小する
→ 「技術そのもの」でなく「アクセスと使い方の分配」が格差の向きを決める""")
