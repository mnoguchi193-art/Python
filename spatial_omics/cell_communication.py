"""
細胞間コミュニケーション / Ligand-receptor cell-cell communication

リガンド-受容体 (L-R) ペアの共発現と細胞の空間的隣接を組み合わせて、
「どの細胞型からどの細胞型へシグナルが伝わりうるか」を推定するデモ。
シグナル伝達には (1) L-R が発現していること と (2) 細胞が物理的に隣接して
いること の両方が必要、という空間オミクス固有の視点を示す。

⚠ 教育目的の合成データ・簡易実装です。
"""

import random
from collections import defaultdict

from synthetic_tissue import GENE_IDX, generate_tissue, knn_graph

t = generate_tissue()
coords, expr, types = t["coords"], t["expr"], t["types"]
n = len(coords)
neighbors = knn_graph(coords, k=6)

# ── L-R データベース / curated ligand-receptor database ──────────────────
# (リガンド, 受容体, 送り手型, 受け手型, 生物学的な意味)
LR_PAIRS = [
    ("CXCL9",  "CXCR3",  "Macrophage",  "T_cell",     "T細胞の遊走/動員"),
    ("SPP1",   "CD44",   "Macrophage",  "Tumor",      "腫瘍関連マクロファージ→腫瘍"),
    ("CXCL13", "CXCR5",  "Fibroblast",  "B_cell",     "B細胞の濾胞形成"),
    ("PDGFB",  "PDGFRB", "Endothelial", "Fibroblast", "血管周囲の間質動員"),
]

# ── 隣接する送り手→受け手ペアで L×R を集計 / spatial L-R scoring ──────────
def communication_score(ligand, receptor, sender_type, receiver_type, labels):
    """空間的に隣接する (送り手, 受け手) 細胞対で ligand×receptor を平均する"""
    li, ri = GENE_IDX[ligand], GENE_IDX[receptor]
    total, edges = 0.0, 0
    for i, nb in enumerate(neighbors):
        if labels[i] != sender_type:
            continue
        for j in nb:
            if labels[j] == receiver_type:
                total += expr[i][li] * expr[j][ri]
                edges += 1
    return (total / edges if edges else 0.0), edges

def adjacency_fraction(sender_type, receiver_type):
    """送り手細胞の全近傍のうち受け手型が占める割合 = 空間的な接触機会"""
    sender_cells = [i for i in range(n) if types[i] == sender_type]
    if not sender_cells:
        return 0.0
    opp = sum(sum(1 for j in neighbors[i] if types[j] == receiver_type)
              for i in sender_cells)
    return opp / (len(sender_cells) * len(neighbors[0]))

# ── 通信スコア = 発現強度 × 空間的隣接 / expression × co-location ─────────
# 順列検定 (z) は「隣接が偶然以上か」を、隣接率は「実際どれだけ接触するか」を測る。
# 通信が実際に成立するには両方 — とくに絶対的な隣接量 — が必要。
PERM = 200
rng = random.Random(1)
shuffled = types[:]

print("ligand-receptor communication (spatially resolved):")
print(f"  {'signal':<16} {'sender→receiver':<25} {'L×R':>5} {'adj':>5} {'z':>6}  status")
results = []
for lig, rec, s, r, meaning in LR_PAIRS:
    obs, edges = communication_score(lig, rec, s, r, types)
    null = []
    for _ in range(PERM):
        rng.shuffle(shuffled)
        null.append(communication_score(lig, rec, s, r, shuffled)[0])
    mu = sum(null) / len(null)
    sd = (sum((x - mu) ** 2 for x in null) / len(null)) ** 0.5 or 1e-9
    z = (obs - mu) / sd
    adj = adjacency_fraction(s, r)
    strength = obs * adj                      # 発現 × 空間 = 実効的な通信強度
    results.append((strength, z, adj, lig, rec, s, r, obs, edges, meaning))

for strength, z, adj, lig, rec, s, r, obs, edges, meaning in sorted(results, reverse=True):
    # 実際に通信が成立 = 隣接が有意 (z>2) かつ絶対的な接触も十分 (adj≥10%)
    status = "✓ active" if (z > 2 and adj >= 0.10) else "· expressed, not co-located"
    print(f"  {lig + '-' + rec:<16} {s + '→' + r:<25} {obs:>5.1f} {adj:>4.0%} {z:>6.1f}  {status}")

# ── 発現 vs 空間の分解 / expression present but not co-located ───────────
print("\nwhy some signals don't fire — expression is necessary but not sufficient:")
for strength, z, adj, lig, rec, s, r, obs, edges, meaning in sorted(results, reverse=True):
    li, ri = GENE_IDX[lig], GENE_IDX[rec]
    lig_expr = sum(expr[i][li] for i in range(n) if types[i] == s) / max(
        1, sum(1 for i in range(n) if types[i] == s))
    rec_expr = sum(expr[i][ri] for i in range(n) if types[i] == r) / max(
        1, sum(1 for i in range(n) if types[i] == r))
    verdict = "signaling" if (z > 2 and adj >= 0.10) else "expressed but cells rarely touch"
    print(f"  {lig}-{rec:<7} [{meaning}]")
    print(f"      ligand={lig_expr:.1f}, receptor={rec_expr:.1f}, "
          f"adjacency={adj:.0%} → {verdict}")

print("""
→ L-R が発現していても、送り手と受け手が空間的に離れていればシグナルは成立しない
  (例: 線維芽細胞の CXCL13 と B細胞の CXCR5 は別ドメインで隣接が乏しい)
→ 逆に腫瘍核ではマクロファージ-腫瘍 (SPP1-CD44)、免疫域ではマクロファージ-T細胞
  (CXCL9-CXCR3) が隣接して活性化 — 組織の場所ごとに異なる通信が働く
→ 「発現 × 空間」を掛け合わせて初めて細胞間通信が読める — 空間オミクスの核心的価値""")
