"""
格差の累積動学 / Cumulative-advantage dynamics of the divide

学力は1年で決まらない。今年の学力が来年の『利用の質』を高め、さらなるゲインを
生む — この正のフィードバック (マタイ効果) が、放任の下では格差を年々広げる。
均等化政策の有無で格差の軌跡がどう分かれるかを複数年シミュレートするデモ。

⚠ 教育目的の簡略モデル。パラメータは説明用の架空値です。
"""

import math

from access_model import access_prob, generate_students, quartile_gap, use_quality

EFFECT = 1.0

def room(level):
    """伸びしろ: 現在の学力が低いほど大きい (補償的)"""
    return 1.0 / (1.0 + math.exp(1.1 * level))

def step_year(students, state, universal_access=False, targeted_support=0.0):
    """1年分の学力更新。state[i] = 現在の学力 (achievement)"""
    new_state = []
    for s, level in zip(students, state):
        access = 1.0 if universal_access else access_prob(s)
        support = targeted_support * 2.0 if (targeted_support and s["ses"] < 0) else targeted_support
        # 利用の質は自己調整力と『現在の学力』に依存 (フィードバックの源)
        srow = dict(s, prior=level)
        quality = use_quality(srow, teacher_support=support)
        gain = EFFECT * room(level) * access * quality
        new_state.append(level + gain)
    return new_state

def gap_over_years(students, years=6, **policy):
    state = [s["prior"] for s in students]
    gaps = []
    for _ in range(years + 1):
        tagged = [dict(s, ach=state[i]) for i, s in enumerate(students)]
        gaps.append(quartile_gap(tagged, "ach")[2])
        state = step_year(students, state, **policy)
    return gaps

students = generate_students()
YEARS = 6

policies = {
    "laissez-faire":                   dict(),
    "universal access":                dict(universal_access=True),
    "universal access + targeted support": dict(universal_access=True, targeted_support=1.0),
}

trajectories = {name: gap_over_years(students, YEARS, **kw) for name, kw in policies.items()}

print(f"SES achievement gap (top vs bottom quartile) over {YEARS} years:")
print(f"  {'policy':<38} " + " ".join(f"Y{y}" for y in range(YEARS + 1)))
for name, gaps in trajectories.items():
    print(f"  {name:<38} " + " ".join(f"{g:>4.2f}" for g in gaps))

# ── 軌跡の可視化 / trajectory bars at start vs end ───────────────────────
hi = max(g for gs in trajectories.values() for g in gs)
print("\ngap width, year 0 vs year 6 (bar length ∝ gap; longer = more unequal):")
for name, gaps in trajectories.items():
    print(f"  {name}")
    print(f"    Y0 {gaps[0]:>4.2f} {'█' * int(gaps[0] / hi * 32)}")
    print(f"    Y6 {gaps[-1]:>4.2f} {'█' * int(gaps[-1] / hi * 32)}")

# ── 初期条件は同じでも軌跡が分岐 / same start, diverging paths ───────────
start = trajectories["laissez-faire"][0]
print(f"\nall policies start from the same gap ({start:.2f}) but diverge:")
for name, gaps in trajectories.items():
    delta = gaps[-1] - gaps[0]
    trend = "widening" if delta > 0.05 else ("narrowing" if delta < -0.05 else "stable")
    print(f"  {name:<38} Y0 {gaps[0]:.2f} → Y{YEARS} {gaps[-1]:.2f}  ({trend})")

print("""
→ 学力→利用の質→ゲインの正のフィードバック (マタイ効果) が格差を自己増殖させる
→ 放任では毎年わずかな差が複利で積み上がり、数年で格差が大きく開く
→ 早期の均等化介入ほど効果が大きい — 累積するからこそ『いつ介入するか』が重要
→ 同じ技術・同じ初期条件でも、分配の設計しだいで格差は開きも縮みもする""")
