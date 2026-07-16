"""
p ハッキングと研究者の自由度 / p-hacking and researcher degrees of freedom

真の効果がゼロ (帰無仮説が正しい) でも、解析の柔軟性 —
逐次的なデータ覗き見 (optional stopping)・複数の従属変数・サブグループ・
共変量選択 — を使えば、名目 5% のはずの偽陽性率が大きく膨らむことを示すデモ。
「分岐する庭 (garden of forking paths)」。

⚠ 教育目的の簡略モデル。すべて真の効果 d=0 (帰無) の下でのシミュレーション。
"""

import math
import random

from study import phi

rng = random.Random(5)
ALPHA = 0.05
TRIALS = 20000

def z_pvalue(sum_a, sum_b, n):
    """既知分散=1 の2群 z 検定の両側 p 値 (各群 n)"""
    if n == 0:
        return 1.0
    z = (sum_a / n - sum_b / n) * math.sqrt(n / 2)
    return 2 * (1 - phi(abs(z)))

# ── (1) 単一検定 (正しい手続き) / a single honest test ───────────────────
def honest(n=40):
    a = sum(rng.gauss(0, 1) for _ in range(n))
    b = sum(rng.gauss(0, 1) for _ in range(n))
    return z_pvalue(a, b, n) < ALPHA

# ── (2) 逐次的な覗き見 / optional stopping ───────────────────────────────
def optional_stopping(n_start=20, n_max=60, batch=5):
    """データを少しずつ増やしながら何度も検定し、有意になったら止める"""
    a = [rng.gauss(0, 1) for _ in range(n_start)]
    b = [rng.gauss(0, 1) for _ in range(n_start)]
    n = n_start
    while True:
        if z_pvalue(sum(a), sum(b), n) < ALPHA:
            return True
        if n >= n_max:
            return False
        for _ in range(batch):
            a.append(rng.gauss(0, 1))
            b.append(rng.gauss(0, 1))
        n += batch

# ── (3) 複数の従属変数 / multiple dependent variables ────────────────────
def multiple_dv(k=5, n=40):
    """k 個の結果指標を測り、どれか1つでも有意なら『発見』とする"""
    for _ in range(k):
        a = sum(rng.gauss(0, 1) for _ in range(n))
        b = sum(rng.gauss(0, 1) for _ in range(n))
        if z_pvalue(a, b, n) < ALPHA:
            return True
    return False

# ── (4) サブグループ解析 / subgroup analysis ─────────────────────────────
def subgroups(n=40, n_sub=4):
    """全体 + いくつかのサブグループを調べ、どれか有意なら報告する"""
    a = [rng.gauss(0, 1) for _ in range(n)]
    b = [rng.gauss(0, 1) for _ in range(n)]
    if z_pvalue(sum(a), sum(b), n) < ALPHA:
        return True
    m = n // n_sub
    for g in range(n_sub):
        sa, sb = a[g * m:(g + 1) * m], b[g * m:(g + 1) * m]
        if len(sa) and z_pvalue(sum(sa), sum(sb), len(sa)) < ALPHA:
            return True
    return False

# ── (5) 全部組み合わせる / the garden of forking paths ───────────────────
def combined():
    """覗き見しつつ、複数DV・サブグループも試す (現実的な柔軟解析)"""
    for _ in range(3):                       # 3つの従属変数
        a = [rng.gauss(0, 1) for _ in range(20)]
        b = [rng.gauss(0, 1) for _ in range(20)]
        n = 20
        while n <= 50:                       # 逐次的に増やす
            if z_pvalue(sum(a), sum(b), n) < ALPHA:
                return True
            half = n // 2                    # サブグループも覗く
            if z_pvalue(sum(a[:half]), sum(b[:half]), half) < ALPHA:
                return True
            for _ in range(5):
                a.append(rng.gauss(0, 1))
                b.append(rng.gauss(0, 1))
            n += 5
    return False

# ── 実行 / run ───────────────────────────────────────────────────────────
def rate(fn, trials=TRIALS):
    return sum(fn() for _ in range(trials)) / trials

print(f"false-positive rate under the NULL (true d=0), nominal α={ALPHA:.0%}:")
print(f"  ({TRIALS:,} simulated experiments each)\n")
practices = [
    ("honest single test",          honest),
    ("optional stopping (peeking)",  optional_stopping),
    ("5 dependent variables",        multiple_dv),
    ("subgroup analysis (+4 groups)", subgroups),
    ("all combined (forking paths)",  combined),
]
print(f"  {'analysis practice':<32} {'false-positive rate':>20}")
for name, fn in practices:
    r = rate(fn)
    bar = "#" * int(r * 60)
    print(f"  {name:<32} {r:>10.0%}  {bar}")

print(f"""
→ どれも真の効果はゼロ。それでも柔軟な解析で偽陽性率は 5% から大きく跳ね上がる
→ 悪意は不要 — 「有意になるまで少し足す」「効いた指標だけ報告」など善意の裁量で起きる
→ p<0.05 という基準は、こうした自由度の下では『発見』をほとんど保証しない
→ だから前登録 (事前に手続きを固定) が再現性の要になる (次モジュール)""")
