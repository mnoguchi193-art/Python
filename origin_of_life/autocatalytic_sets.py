"""
自己触媒集合 / Autocatalytic (RAF) sets — the metabolism-first view

Kauffman の自己触媒集合を、Hordijk-Steel の RAF アルゴリズムで解析するデモ。
ランダムな『化学』(分子=文字列、反応=連結、触媒=ランダム割当) を作り、
食物集合から出発して自己触媒的に閉じた反応集合 (RAF) を探す。
分子あたりの触媒数がある閾値を超えると、大きな RAF が突然出現する
(パーコレーション的な相転移) — 集団的自己触媒が『無料で』生じることを示す。

RAF = Reflexively Autocatalytic and Food-generated:
  集合内の全反応が、集合が生み出す分子によって触媒され、かつ
  全反応物が食物集合から生成可能である、そんな反応集合。

⚠ 教育目的の簡略モデルです。
"""

import random

# ── ランダムな化学の構築 / build a random polymer chemistry ──────────────
ALPHABET = "ab"
MAXLEN = 6

def all_molecules(maxlen=MAXLEN):
    mols = []
    for L in range(1, maxlen + 1):
        for i in range(len(ALPHABET) ** L):
            s, x = "", i
            for _ in range(L):
                s += ALPHABET[x % len(ALPHABET)]
                x //= len(ALPHABET)
            mols.append(s)
    return mols

def ligation_reactions(molecules, maxlen=MAXLEN):
    """連結反応 r + s → rs (長さが maxlen 以下) を列挙"""
    reactions = []
    for r in molecules:
        for s in molecules:
            if len(r) + len(s) <= maxlen:
                reactions.append(((r, s), r + s))
    return reactions

# ── RAF アルゴリズム / the RAF algorithm (Hordijk & Steel 2004) ──────────
def food_closure(reactions, active, food):
    """集合 active の反応 (反応物が揃うもの) で食物から作れる分子の閉包"""
    closure = set(food)
    changed = True
    while changed:
        changed = False
        for rid in active:
            (a, b), prod = reactions[rid]
            if prod not in closure and a in closure and b in closure:
                closure.add(prod)
                changed = True
    return closure

def maximal_raf(reactions, catalysts, food):
    """最大 RAF を返す (空集合なら自己触媒的閉包なし)。
    反応物支持で閉包を計算 → 触媒が閉包内にない反応を除去 → 収束まで反復。"""
    active = set(range(len(reactions)))
    while True:
        closure = food_closure(reactions, active, food)
        new_active = {
            rid for rid in active
            if reactions[rid][0][0] in closure and reactions[rid][0][1] in closure
            and any(c in closure for c in catalysts[rid])
        }
        if new_active == active:
            return active, closure
        active = new_active

# ── 触媒割当と相転移の観察 / random catalysis and the phase transition ───
def assign_catalysts(reactions, molecules, prob, rng):
    """各 (分子, 反応) 対に確率 prob で触媒作用を与える"""
    catalysts = []
    for _ in reactions:
        cats = [m for m in molecules if rng.random() < prob]
        catalysts.append(cats)
    return catalysts

MOLS = all_molecules()
REACTIONS = ligation_reactions(MOLS)
FOOD = set(m for m in MOLS if len(m) <= 2)   # 食物: 長さ2以下は常に供給される

print(f"random chemistry: {len(MOLS)} molecules (len ≤ {MAXLEN}), "
      f"{len(REACTIONS)} ligation reactions, {len(FOOD)} food molecules")

print("\nemergence of a collectively autocatalytic set (RAF):")
print(f"  {'catalysis/molecule':>18} {'P(RAF exists)':>14} {'mean RAF size':>14}")
TRIALS = 30
for f_target in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
    prob = f_target / len(REACTIONS)          # 分子あたり平均 f_target 反応を触媒
    nonempty, sizes = 0, []
    for seed in range(TRIALS):
        rng = random.Random(seed)
        cats = assign_catalysts(REACTIONS, MOLS, prob, rng)
        raf, _ = maximal_raf(REACTIONS, cats, FOOD)
        if raf:
            nonempty += 1
            sizes.append(len(raf))
    mean_size = sum(sizes) / len(sizes) if sizes else 0
    bar = "#" * int(nonempty / TRIALS * 30)
    print(f"  {f_target:>18.1f} {nonempty / TRIALS:>13.0%} {mean_size:>14.1f}  {bar}")

print("→ 分子あたり ~1-2 反応を触媒するあたりで、RAF が急に出現する (相転移)")
print("→ 個々の分子は弱い触媒でも、集団として『自分たちを作る』閉じた輪が生まれる")

# ── 具体例の中身 / anatomy of one RAF ────────────────────────────────────
rng = random.Random(2)
cats = assign_catalysts(REACTIONS, MOLS, 2.5 / len(REACTIONS), rng)
raf, closure = maximal_raf(REACTIONS, cats, FOOD)
print(f"\nexample RAF (catalysis≈2.5/mol): {len(raf)} reactions, "
      f"{len(closure)} molecules producible from food")
if raf:
    for rid in list(raf)[:6]:
        (a, b), prod = REACTIONS[rid]
        cat_in = [c for c in cats[rid] if c in closure]
        print(f"  {a} + {b} → {prod}   (catalysed by {cat_in[0] if cat_in else '?'})")
    if len(raf) > 6:
        print(f"  ... and {len(raf) - 6} more reactions, all mutually supported")

print("""
→ 代謝優先 (metabolism-first) の考え: 生命はまず『集団的自己触媒』として始まった
→ 遺伝子や鋳型がなくても、反応網が閾値を超えれば自己維持する輪が創発する
→ 情報を運ぶ複製 (次モジュール) と、この自己触媒代謝の統合が生命への道筋""")
