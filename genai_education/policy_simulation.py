"""
政策シミュレーション / Policy levers to close the gap

格差を縮める複数の政策レバーを個別・組み合わせで評価し、「格差縮小 (公平)」と
「全体の平均ゲイン (効率)」の両面で比較するデモ。公平と効率は必ずしも
トレードオフでないこと、レバーの組み合わせが鍵であることを示す。

⚠ 教育目的の簡略モデル。パラメータは説明用の架空値です。
"""

import math

from access_model import generate_students, logistic, quartile_gap

EFFECT = 1.2

def room(prior):
    return 1.0 / (1.0 + math.exp(1.1 * prior))

# ── 政策レバー / policy levers ───────────────────────────────────────────
# 各レバーがアクセス・利用の質のパラメータをどう変えるか。
LEVERS = {
    "subsidized_access":  "端末・通信・有料版の補助 (アクセスの底上げ)",
    "prompt_literacy":    "AIリテラシー教育 (全員の利用の質を底上げ)",
    "teacher_support":    "教員の指導支援 (低SES層の利用の質を重点的に)",
    "guardrailed_tools":  "足場かけ型ツール (自己調整力が低い生徒を保護)",
}

def outcomes(students, levers):
    """有効なレバー集合の下で、genAI 導入後の学力を計算"""
    res = []
    for s in students:
        # アクセス
        a_int = 0.3 + (1.5 if "subsidized_access" in levers else 0.0)
        access = logistic(a_int + 0.9 * s["home"] + 0.6 * s["school"])
        # 利用の質
        q = -0.2 + 0.6 * s["selfreg"] + 0.4 * s["prior"]
        if "prompt_literacy" in levers:
            q += 0.7
        if "teacher_support" in levers and s["ses"] < 0:
            q += 1.4                                  # 低SES層に重点
        if "guardrailed_tools" in levers:
            q += 0.9 * (1.0 - logistic(s["selfreg"]))  # 自己調整力が低いほど恩恵
        quality = logistic(q)
        gain = EFFECT * room(s["prior"]) * access * quality
        res.append(dict(s, achievement=s["prior"] + gain, gain=gain))
    return res

students = generate_students()
base = [dict(s, achievement=s["prior"]) for s in students]
_, _, base_gap = quartile_gap(base, "achievement")

def evaluate(levers):
    res = outcomes(students, levers)
    _, _, gap = quartile_gap(res, "achievement")
    mean_gain = sum(r["gain"] for r in res) / len(res)
    # 低SES層 (下位25%) の平均ゲイン
    low = sorted(res, key=lambda r: r["ses"])[:len(res) // 4]
    low_gain = sum(r["gain"] for r in low) / len(low)
    return gap, mean_gain, low_gain

# ── 個別レバーの効果 / single-lever effects ──────────────────────────────
print(f"baseline gap (no genAI): {base_gap:.2f}\n")
print("single policy levers:")
print(f"  {'lever':<20} {'gap':>5} {'Δgap':>6} {'mean gain':>10} {'low-SES gain':>13}")
g0, m0, l0 = evaluate(set())
print(f"  {'laissez-faire':<20} {g0:>5.2f} {g0 - base_gap:>+6.2f} {m0:>10.2f} {l0:>13.2f}")
for lever, desc in LEVERS.items():
    g, m, l = evaluate({lever})
    print(f"  {lever:<20} {g:>5.2f} {g - base_gap:>+6.2f} {m:>10.2f} {l:>13.2f}")

# ── 組み合わせ / combinations ────────────────────────────────────────────
print("\npolicy packages:")
packages = {
    "access only":            {"subsidized_access"},
    "access + literacy":      {"subsidized_access", "prompt_literacy"},
    "access + targeted teach": {"subsidized_access", "teacher_support"},
    "full package (all 4)":   set(LEVERS),
}
print(f"  {'package':<24} {'gap':>5} {'Δgap':>6} {'mean gain':>10} {'low-SES gain':>13}")
for name, levers in packages.items():
    g, m, l = evaluate(levers)
    print(f"  {name:<24} {g:>5.2f} {g - base_gap:>+6.2f} {m:>10.2f} {l:>13.2f}")

# ── 公平と効率の両立 / equity and efficiency together ────────────────────
gf, mf, lf = evaluate(set(LEVERS))
print(f"""
→ 単独レバーでは限界がある。アクセス補助だけでは利用の質の格差が残る
→ 『アクセス + 低SES層への指導支援』の組み合わせが最も格差を縮める
→ フルパッケージは格差を {base_gap:.2f}→{gf:.2f} に縮めつつ、平均ゲインも最大化
  — 公平 (格差縮小) と効率 (全体の伸び) はトレードオフではなく両立しうる
→ 鍵は『底上げ』の設計: 誰がアクセスでき、どう使いこなせるかを政策で均すこと""")
