"""
原始細胞と多段階選択 / Protocells and multilevel selection

区画化 (膜で仕切ること) がなぜ生命の起源に重要かを示すデモ。
細胞内では『速く複製する寄生的な複製子』が協力的な複製子を駆逐する
(共有地の悲劇)。しかし協力者を多く含む細胞ほど速く成長・分裂するため、
細胞間の選択が細胞内の選択に対抗できる — 区画化が協力を救う。

⚠ 教育目的の簡略な確率モデルです。
"""

import random

rng = random.Random(7)

M_CELLS = 400          # 原始細胞の数
N_MOLS = 20            # 1細胞内の複製子数 (少ないほど分裂時のばらつき大)
S_WITHIN = 0.35        # 細胞内での寄生子の複製優位 / parasite's within-cell edge
MUTATION = 0.03        # 協力者→寄生子への変異率 (寄生子を再導入し完全固定を防ぐ)
GENERATIONS = 50

def within_cell(p):
    """細胞内選択 (寄生子が有利で p が下がる) + 変異による寄生子の再導入"""
    p = p / (p + (1 - p) * (1 + S_WITHIN))
    return p * (1 - MUTATION)

def divide(p):
    """分裂時のランダムな分配 (二項サンプリング) — 細胞間のばらつきを生む"""
    coop = sum(1 for _ in range(N_MOLS) if rng.random() < p)
    return coop / N_MOLS

def step(cells, compartment_selection):
    # 1) 細胞内選択 (寄生子が増える)
    cells = [within_cell(p) for p in cells]
    # 2) 分裂 + ランダム分配 (細胞間のばらつきを再生)
    cells = [divide(p) for p in cells]
    # 3) 細胞間選択: 協力者を多く含む細胞ほど分裂に成功する
    if compartment_selection:
        weights = [p + 0.01 for p in cells]        # 細胞適応度 ∝ 協力者割合
        total = sum(weights)
        cells = [cells[_weighted_pick(weights, total)] for _ in range(len(cells))]
    else:
        cells = [cells[rng.randrange(len(cells))] for _ in range(len(cells))]  # 無選択
    return cells

def _weighted_pick(weights, total):
    r, acc = rng.random() * total, 0.0
    for i, w in enumerate(weights):
        acc += w
        if r < acc:
            return i
    return len(weights) - 1

def run(compartment_selection, p0=0.6):
    cells = [p0 for _ in range(M_CELLS)]
    traj = [sum(cells) / len(cells)]
    for _ in range(GENERATIONS):
        cells = step(cells, compartment_selection)
        traj.append(sum(cells) / len(cells))
    return traj

with_comp = run(True)
without_comp = run(False)

print("mean cooperator fraction over generations:")
print(f"  {'generation':>10} " + " ".join(f"{g:>3}" for g in range(0, GENERATIONS + 1, 10)))
print(f"  {'with compartments':>18} " +
      " ".join(f"{with_comp[g]:>3.0%}" for g in range(0, GENERATIONS + 1, 10)))
print(f"  {'no compartments':>18} " +
      " ".join(f"{without_comp[g]:>3.0%}" for g in range(0, GENERATIONS + 1, 10)))

print("\ntrajectory (cooperator fraction; █ high, ▄ mid, · low):")
for label, traj in [("with compartments", with_comp), ("no compartments  ", without_comp)]:
    spark = "".join("█" if v > 0.5 else ("▄" if v > 0.2 else "·") for v in traj)
    print(f"  {label} |{spark}| final {traj[-1]:.0%}")

print(f"""
→ 区画なし: 細胞内選択だけが働き、寄生的な複製子が協力者を駆逐する ({without_comp[-1]:.0%})
→ 区画あり: 協力者の多い細胞が選択されて生き残り、協力が維持される ({with_comp[-1]:.0%})
→ 膜による区画化は、分子どうしの利害を『細胞』というより高い単位にそろえる
→ 分裂時のランダムな分配が細胞間の多様性を生み、細胞レベルの選択を可能にする
→ 原始細胞 (protocell) は、複製子の協力と情報を守る『器』として生命の起源に不可欠""")
