"""
生徒集団とアクセス格差 / Student population and the access divide

生成AI (genAI) と教育格差を分析するための共有コア。社会経済的地位 (SES) と
相関する属性 (家庭資源・学校資源・事前学力・自己調整学習力) を持つ生徒集団を
生成し、genAI ツールへのアクセス確率と利用の質をモデル化する。

⚠ 教育目的の簡略モデル。パラメータは説明用の架空値で、実証データではありません。
"""

import math
import random

# ── ロジスティック関数 / logistic ────────────────────────────────────────
def logistic(x):
    return 1.0 / (1.0 + math.exp(-x))

# ── 生徒集団の生成 / generate a student population ───────────────────────
# 潜在的な SES が、相関する複数の属性を駆動する (すべて標準化スケール)。
def generate_students(n=2000, seed=11):
    rng = random.Random(seed)
    students = []
    for _ in range(n):
        ses = rng.gauss(0, 1)                                   # 社会経済的地位
        home = 0.70 * ses + rng.gauss(0, 0.7)                   # 家庭のICT/学習資源
        school = 0.50 * ses + rng.gauss(0, 0.8)                 # 学校の資源・指導力
        prior = 0.45 * ses + 0.25 * home + rng.gauss(0, 0.7)    # 事前学力
        selfreg = 0.30 * ses + rng.gauss(0, 0.9)               # 自己調整学習力
        students.append(dict(ses=ses, home=home, school=school,
                             prior=prior, selfreg=selfreg))
    return students

# ── アクセス確率 / probability of access to genAI tools ──────────────────
# デバイス・通信・有料版・学校の許可などが家庭/学校資源に依存する。
def access_prob(s, intercept=0.3, w_home=0.9, w_school=0.6):
    return logistic(intercept + w_home * s["home"] + w_school * s["school"])

# ── 利用の質 / quality of use (0-1) ──────────────────────────────────────
# 同じツールでも、足場かけ (scaffold) として使うか、丸投げ (offload) するかで
# 学習効果が変わる。自己調整力・事前学力・指導支援に依存する。
def use_quality(s, teacher_support=0.0, w_selfreg=0.6, w_prior=0.4):
    return logistic(-0.2 + w_selfreg * s["selfreg"] + w_prior * s["prior"]
                    + teacher_support)

# ── 格差の指標 / inequality metrics ──────────────────────────────────────
def quartile_gap(students, key):
    """SES 上位25%と下位25%での平均差 (key の値)"""
    ranked = sorted(students, key=lambda s: s["ses"])
    q = len(ranked) // 4
    bottom = sum(s[key] for s in ranked[:q]) / q
    top = sum(s[key] for s in ranked[-q:]) / q
    return top, bottom, top - bottom

def correlation(students, key_a, key_b):
    n = len(students)
    a = [s[key_a] for s in students]
    b = [s[key_b] for s in students]
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / n
    sa = (sum((x - ma) ** 2 for x in a) / n) ** 0.5
    sb = (sum((y - mb) ** 2 for y in b) / n) ** 0.5
    return cov / (sa * sb) if sa and sb else 0.0

# ── デモ / demo ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    students = generate_students()
    for s in students:
        s["access"] = access_prob(s)
        s["quality"] = use_quality(s)

    n = len(students)
    print(f"student population: {n}")
    print(f"SES–prior achievement correlation: {correlation(students, 'ses', 'prior'):.2f}")

    print("\naccess to genAI tools by SES quartile:")
    ranked = sorted(students, key=lambda s: s["ses"])
    for i, name in enumerate(["Q1 (lowest SES)", "Q2", "Q3", "Q4 (highest)"]):
        grp = ranked[i * n // 4:(i + 1) * n // 4]
        acc = sum(s["access"] for s in grp) / len(grp)
        qual = sum(s["quality"] for s in grp) / len(grp)
        print(f"  {name:<16} access {acc:>4.0%}  |  use-quality {qual:>4.0%}  "
              f"{'#' * int(acc * 30)}")

    ta, ba, ga = quartile_gap(students, "access")
    tq, bq, gq = quartile_gap(students, "quality")
    print(f"\naccess gap  (top - bottom quartile): {ga:+.0%}")
    print(f"use-quality gap (top - bottom):      {gq:+.0%}")
    print("\n→ アクセス格差 (第一のデジタル・デバイド) に加え、")
    print("  『使いこなしの質』の格差 (第二のデバイド) が重なる")
    print("→ 高SES層はアクセスも利用の質も高い — 均せなければ格差を広げうる")
