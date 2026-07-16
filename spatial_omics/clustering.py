"""
発現によるクラスタリング / Unsupervised cell-type clustering

発現プロファイルだけから細胞を教師なしでクラスタリング (k-means) し、
正解の細胞型ラベルと ARI (調整ランド指数) で比較、各クラスタのマーカー遺伝子を
同定するデモ。空間情報を使わずに「細胞型」を復元できることを示す。

⚠ 教育目的の合成データ・簡易実装です。
"""

import random
from collections import Counter, defaultdict

from synthetic_tissue import CELL_TYPES, generate_tissue

# ── 前処理: 遺伝子ごとの z-score / standardize each gene ──────────────────
def zscore(expr):
    n, g = len(expr), len(expr[0])
    means = [sum(row[j] for row in expr) / n for j in range(g)]
    stds = []
    for j in range(g):
        var = sum((row[j] - means[j]) ** 2 for row in expr) / n
        stds.append(var ** 0.5 or 1.0)
    return [[(row[j] - means[j]) / stds[j] for j in range(g)] for row in expr]

# ── k-means (Lloyd 法, 複数初期値) / k-means from scratch ─────────────────
def _dist2(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))

def kmeans(data, k, seed=0, restarts=6, iters=50):
    best_labels, best_inertia = None, float("inf")
    for r in range(restarts):
        rng = random.Random(seed + r)
        centers = [data[i][:] for i in rng.sample(range(len(data)), k)]
        labels = [0] * len(data)
        for _ in range(iters):
            changed = False
            for i, row in enumerate(data):
                lab = min(range(k), key=lambda c: _dist2(row, centers[c]))
                if lab != labels[i]:
                    labels[i], changed = lab, True
            groups = defaultdict(list)
            for i, lab in enumerate(labels):
                groups[lab].append(data[i])
            for c in range(k):
                if groups[c]:
                    centers[c] = [sum(col) / len(groups[c]) for col in zip(*groups[c])]
            if not changed:
                break
        inertia = sum(_dist2(data[i], centers[labels[i]]) for i in range(len(data)))
        if inertia < best_inertia:
            best_labels, best_inertia = labels[:], inertia
    return best_labels

# ── 調整ランド指数 / adjusted Rand index ─────────────────────────────────
def adjusted_rand_index(true, pred):
    def comb2(x):
        return x * (x - 1) // 2
    contingency = defaultdict(int)
    for a, b in zip(true, pred):
        contingency[(a, b)] += 1
    a_counts, b_counts = Counter(true), Counter(pred)
    sum_ij = sum(comb2(v) for v in contingency.values())
    sum_a = sum(comb2(v) for v in a_counts.values())
    sum_b = sum(comb2(v) for v in b_counts.values())
    n = len(true)
    expected = sum_a * sum_b / comb2(n)
    max_index = (sum_a + sum_b) / 2
    return (sum_ij - expected) / (max_index - expected) if max_index != expected else 1.0

# ── 実行 / run ───────────────────────────────────────────────────────────
import math

if __name__ == "__main__":
    t = generate_tissue()
    data = zscore(t["expr"])
    K = len(CELL_TYPES)
    labels = kmeans(data, K, seed=1)

    ari = adjusted_rand_index(t["types"], labels)
    print(f"clustered {len(data)} cells into {K} clusters (expression only, no spatial info)")
    print(f"adjusted Rand index vs ground truth: {ari:.3f} "
          f"({'excellent' if ari > 0.8 else 'good' if ari > 0.6 else 'fair'})")

    # ── クラスタ→細胞型の対応と純度 / map clusters to types ──────────────
    print("\ncluster composition (majority-vote label):")
    print(f"  {'cluster':>7} {'n':>4} {'purity':>7}  dominant type")
    for c in range(K):
        idx = [i for i in range(len(labels)) if labels[i] == c]
        if not idx:
            continue
        comp = Counter(t["types"][i] for i in idx)
        dom, cnt = comp.most_common(1)[0]
        print(f"  {c:>7} {len(idx):>4} {cnt / len(idx):>6.0%}  {dom}")

    # ── マーカー遺伝子の同定 / marker gene discovery per cluster ──────────
    genes = t["genes"]
    overall = [sum(row[j] for row in t["expr"]) / len(t["expr"]) for j in range(len(genes))]
    print("\ntop markers per cluster (log fold-change vs overall mean):")
    for c in range(K):
        idx = [i for i in range(len(labels)) if labels[i] == c]
        if not idx:
            continue
        means = [sum(t["expr"][i][j] for i in idx) / len(idx) for j in range(len(genes))]
        lfc = sorted(((math.log2((means[j] + 0.1) / (overall[j] + 0.1)), genes[j])
                      for j in range(len(genes))), reverse=True)
        dom = Counter(t["types"][i] for i in idx).most_common(1)[0][0]
        top = ", ".join(f"{g}(+{v:.1f})" for v, g in lfc[:3])
        print(f"  cluster {c} [{dom:<11}]: {top}")

    print("\n→ 空間情報を使わずとも、発現プロファイルだけで細胞型はほぼ復元できる")
    print("→ 同定したマーカーは既知の細胞型マーカーと一致 (EPCAM=上皮, CD3D=T細胞 …)")
    print("→ 空間オミクスの強みは、細胞型に『どこにいるか』を重ねられること (次モジュール)")
