"""
空間統計 / Spatial statistics: variable genes and neighborhood enrichment

空間オミクス固有の解析を2つ実装するデモ:
(1) Moran's I による「空間的に変動する遺伝子 (spatially variable genes)」の検出、
(2) 近傍エンリッチメント — どの細胞型どうしが偶然以上に隣接しているか
    (順列検定で有意性を評価)。

⚠ 教育目的の合成データ・簡易実装です。
"""

import random
from collections import defaultdict

from synthetic_tissue import CELL_TYPES, generate_tissue, knn_graph

t = generate_tissue()
coords, expr, types, genes = t["coords"], t["expr"], t["types"], t["genes"]
n = len(coords)
neighbors = knn_graph(coords, k=6)

# ── Moran's I / 空間的自己相関 ────────────────────────────────────────────
# I = (N/W)·ΣΣ w_ij (x_i-x̄)(x_j-x̄) / Σ(x_i-x̄)²
# w_ij は kNN の二値重み。I>0 で空間的にまとまり、≈0 でランダム分布。
def morans_i(values, neighbors):
    mean = sum(values) / len(values)
    dev = [v - mean for v in values]
    denom = sum(d * d for d in dev) or 1e-9
    num, W = 0.0, 0
    for i, nb in enumerate(neighbors):
        for j in nb:
            num += dev[i] * dev[j]
            W += 1
    return (len(values) / W) * (num / denom)

print("spatially variable genes (Moran's I, top = most spatially structured):")
scores = []
for gj in range(len(genes)):
    vals = [expr[i][gj] for i in range(n)]
    scores.append((morans_i(vals, neighbors), genes[gj]))
scores.sort(reverse=True)
for I, g in scores[:8]:
    bar = "#" * int(max(I, 0) * 40)
    print(f"  {g:<8} I={I:+.3f}  {bar}")
print("  ...")
for I, g in scores[-3:]:
    print(f"  {g:<8} I={I:+.3f}  (spatially random)")
print("→ GRAD_X/Y (座標勾配) と、空間的に固まった細胞型のマーカーが高い I を示す")
print("→ 背景ノイズ遺伝子は I≈0。空間構造を持つ遺伝子だけを統計的に選び出せる")

# ── 近傍エンリッチメント / neighborhood enrichment ───────────────────────
# 観測された「型A-型B の隣接回数」を、ラベルをシャッフルした帰無分布と比較し
# z スコアを出す。z>0 で共局在、z<0 で棲み分け (相互排他)。
type_list = sorted(CELL_TYPES)

def adjacency_counts(labels):
    counts = defaultdict(int)
    for i, nb in enumerate(neighbors):
        for j in nb:
            a, b = labels[i], labels[j]
            key = tuple(sorted((a, b)))
            counts[key] += 1
    return counts

observed = adjacency_counts(types)

# 順列検定 / permutation null
PERM = 200
null = defaultdict(list)
rng = random.Random(0)
shuffled = types[:]
for _ in range(PERM):
    rng.shuffle(shuffled)
    c = adjacency_counts(shuffled)
    for key in c:
        null[key].append(c[key])

def zscore(key):
    samples = null.get(key, [0])
    mu = sum(samples) / len(samples)
    var = sum((s - mu) ** 2 for s in samples) / len(samples)
    sd = var ** 0.5 or 1.0
    return (observed.get(key, 0) - mu) / sd

pairs = []
for i, a in enumerate(type_list):
    for b in type_list[i:]:
        pairs.append((zscore(tuple(sorted((a, b)))), a, b))
pairs.sort(reverse=True)

print("\nneighborhood enrichment (z-score; + co-localized, - segregated):")
print("  most co-localized:")
for z, a, b in pairs[:5]:
    print(f"    {a:<11} — {b:<11} z={z:+6.1f}  {'#' * int(max(z, 0))}")
print("  most segregated:")
for z, a, b in pairs[-4:]:
    print(f"    {a:<11} — {b:<11} z={z:+6.1f}")

print("""
→ 腫瘍-マクロファージ、T細胞-B細胞など、同じドメインに共存する型が高い z を示す
→ 腫瘍と間質 (線維芽細胞) のように別ドメインの型は負の z (棲み分け)
→ 「どの細胞型が物理的に隣り合うか」は、細胞型の同定だけでは得られない
  空間オミクス固有の情報 — 組織の設計図を読み解く鍵になる""")
