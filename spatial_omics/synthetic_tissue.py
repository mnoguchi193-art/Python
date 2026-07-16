"""
合成組織データの生成 / Synthetic spatial-omics tissue

単一細胞空間オミクスの解析デモ用に、空間座標・遺伝子発現・細胞型 (正解ラベル)
を持つ「組織切片」を生成する共有コア。腫瘍核・免疫浸潤・間質の3ドメインに
細胞型を配置し、マーカー遺伝子の発現と空間的な勾配遺伝子を作り込む。
kNN 近傍グラフのユーティリティも提供する。

⚠ 教育目的の合成データです。実データ (Visium, MERFISH, Xenium 等) の
   統計的性質を厳密に再現するものではありません。
"""

import math
import random

# ── 遺伝子とマーカー / genes and markers ─────────────────────────────────
GENES = [
    "EPCAM", "KRT8", "MKI67",        # 上皮/腫瘍
    "CD3D", "CD8A", "IL7R",          # T細胞
    "CD19", "MS4A1", "IGHG1",        # B細胞/形質細胞
    "CD68", "LYZ", "C1QA",           # マクロファージ
    "COL1A1", "PDGFRB", "ACTA2",     # 線維芽細胞
    "PECAM1", "VWF", "CLDN5",        # 内皮
    # リガンド/受容体 (細胞間コミュニケーション用) / ligands & receptors
    "CXCL9", "CXCR3", "SPP1", "CD44", "CXCL13", "CXCR5", "PDGFB",
    "GRAD_X", "GRAD_Y",              # 空間勾配遺伝子 (細胞型に非依存)
]
GENE_IDX = {g: i for i, g in enumerate(GENES)}

# リガンド/受容体を発現する細胞型と発現量 / L-R source type and level
# (PDGFRB は線維芽細胞マーカーを受容体として再利用)
LR_SOURCES = {
    "CXCL9": ("Macrophage", 3.5), "CXCR3": ("T_cell", 3.0),
    "SPP1": ("Macrophage", 3.5),  "CD44": ("Tumor", 3.0),
    "CXCL13": ("Fibroblast", 3.0), "CXCR5": ("B_cell", 3.0),
    "PDGFB": ("Endothelial", 3.0),
}

# 細胞型 → 高発現するマーカー / cell type → high-expression markers
CELL_TYPES = {
    "Tumor":       ["EPCAM", "KRT8", "MKI67"],
    "T_cell":      ["CD3D", "CD8A", "IL7R"],
    "B_cell":      ["CD19", "MS4A1", "IGHG1"],
    "Macrophage":  ["CD68", "LYZ", "C1QA"],
    "Fibroblast":  ["COL1A1", "PDGFRB", "ACTA2"],
    "Endothelial": ["PECAM1", "VWF", "CLDN5"],
}

# 空間ドメイン → 細胞型の構成比 / domain → cell-type composition
DOMAINS = {
    "tumor_core":     {"Tumor": 0.70, "Macrophage": 0.20, "Endothelial": 0.10},
    "immune_infiltrate": {"T_cell": 0.45, "B_cell": 0.35, "Macrophage": 0.20},
    "stroma":         {"Fibroblast": 0.60, "Endothelial": 0.25, "T_cell": 0.15},
}

FIELD = 100.0  # 組織の一辺 (µm 相当)

def _domain_of(x, y):
    """座標からドメインを決める: 中心=腫瘍核、その周囲=免疫浸潤、外側=間質"""
    r = math.hypot(x - FIELD / 2, y - FIELD / 2)
    if r < 22:
        return "tumor_core"
    if r < 38:
        return "immune_infiltrate"
    return "stroma"

def _sample_type(comp, rng):
    r, acc = rng.random(), 0.0
    for ct, frac in comp.items():
        acc += frac
        if r < acc:
            return ct
    return list(comp)[-1]

def generate_tissue(n_cells=700, seed=7, noise=1.1, marker_level=4.0, dropout=0.25):
    """組織を生成し、coords / expr / types / domains を返す。

    dropout: 各発現値が技術的に検出されずゼロになる確率 (単一細胞データ特有の
    「ドロップアウト」)。マーカーが時に落ちるためクラスタリングが現実的な難度になる。
    """
    rng = random.Random(seed)
    coords, types, domains, expr = [], [], [], []
    for _ in range(n_cells):
        x, y = rng.uniform(0, FIELD), rng.uniform(0, FIELD)
        dom = _domain_of(x, y)
        ct = _sample_type(DOMAINS[dom], rng)
        # 発現ベクトル: 基礎発現 + 自型マーカーの上昇 + ノイズ
        vec = [max(0.0, rng.gauss(0.5, noise * 0.4)) for _ in GENES]
        for m in CELL_TYPES[ct]:
            vec[GENE_IDX[m]] = max(0.0, rng.gauss(marker_level, noise))
        # この細胞型が発現するリガンド/受容体を上げる
        for gene, (src_type, level) in LR_SOURCES.items():
            if src_type == ct:
                vec[GENE_IDX[gene]] = max(0.0, rng.gauss(level, noise))
        # 空間勾配遺伝子: 座標に比例 (細胞型に依存しない空間的発現)
        vec[GENE_IDX["GRAD_X"]] = max(0.0, 6.0 * x / FIELD + rng.gauss(0, noise * 0.3))
        vec[GENE_IDX["GRAD_Y"]] = max(0.0, 6.0 * y / FIELD + rng.gauss(0, noise * 0.3))
        # ドロップアウト: 空間勾配遺伝子以外に適用
        for j in range(len(GENES) - 2):
            if rng.random() < dropout:
                vec[j] = 0.0
        coords.append((x, y))
        types.append(ct)
        domains.append(dom)
        expr.append(vec)
    return dict(coords=coords, expr=expr, types=types, domains=domains, genes=GENES)

# ── 空間近傍グラフ / spatial neighbor graph ──────────────────────────────
def knn_graph(coords, k=6):
    """各細胞の k 最近傍のインデックスを返す (総当たり; N が小さいので十分)"""
    n = len(coords)
    neighbors = []
    for i in range(n):
        xi, yi = coords[i]
        dists = sorted(
            ((math.hypot(xi - coords[j][0], yi - coords[j][1]), j)
             for j in range(n) if j != i),
            key=lambda t: t[0],
        )
        neighbors.append([j for _, j in dists[:k]])
    return neighbors

# ── デモ / demo ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    t = generate_tissue()
    n = len(t["coords"])
    print(f"generated tissue: {n} cells, {len(GENES)} genes, "
          f"{len(CELL_TYPES)} cell types, {len(DOMAINS)} spatial domains")

    from collections import Counter
    print("\ncell-type composition:")
    for ct, c in Counter(t["types"]).most_common():
        print(f"  {ct:<12} {c:>4}  {'#' * (c * 40 // n)}")

    print("\ncell types by spatial domain:")
    for dom in DOMAINS:
        idx = [i for i in range(n) if t["domains"][i] == dom]
        comp = Counter(t["types"][i] for i in idx)
        top = ", ".join(f"{ct} {c * 100 // len(idx)}%" for ct, c in comp.most_common(3))
        print(f"  {dom:<18} ({len(idx):>3} cells): {top}")

    # 空間分布の ASCII マップ / ASCII map of the tissue
    print("\nspatial map (T=Tumor, I=immune, F=Fibroblast, E=Endo, .=other):")
    letter = {"Tumor": "T", "T_cell": "I", "B_cell": "I", "Macrophage": "m",
              "Fibroblast": "F", "Endothelial": "E"}
    grid = [[" "] * 40 for _ in range(20)]
    for (x, y), ct in zip(t["coords"], t["types"]):
        gx, gy = int(x / FIELD * 39), int(y / FIELD * 19)
        grid[gy][gx] = letter.get(ct, ".")
    for row in grid:
        print("  " + "".join(row))
    print("→ 中心の腫瘍核 (T) を免疫細胞 (I) が取り囲み、外側は間質 (F/E) — 空間構造を持つ")
