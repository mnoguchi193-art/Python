"""
幹細胞からβ細胞への分化 / Directed differentiation: stem cells → islet β-cells

多能性幹細胞 (iPSC/ESC) を段階的に膵島β細胞へ分化させるプロトコルの
「段階ごとの収率」をモデル化し、最終的なβ細胞の得率・1回投与に必要な
出発細胞数・オフターゲット細胞の割合を試算するデモ。

⚠ 教育目的の簡略モデル。段階効率は説明用の架空値です (実プロトコルは
   Pagliuca 2014 / Rezania 2014 などの多段階分化に基づく)。
"""

from dataclasses import dataclass

# ── 分化の各段階 / differentiation stages ────────────────────────────────
# 各段階で「次の目的細胞へ進む割合 (yield)」と「日数」を持つ。
# 残りは前段階に留まる・死ぬ・オフターゲット (別系統) に逸れる。
@dataclass
class Stage:
    name: str
    yield_frac: float   # 目的の次段階へ進む割合 / fraction advancing on-target
    days: int
    death_frac: float   # この段階で死ぬ割合 / apoptosis during stage

STAGES = [
    Stage("pluripotent → definitive endoderm", 0.85, 3, 0.10),
    Stage("→ primitive gut tube",              0.90, 2, 0.05),
    Stage("→ posterior foregut",               0.80, 2, 0.08),
    Stage("→ pancreatic endoderm (PDX1+)",     0.75, 3, 0.10),
    Stage("→ endocrine progenitor (NGN3+)",    0.65, 3, 0.12),
    Stage("→ immature β-cell",                 0.60, 4, 0.10),
    Stage("→ mature β-cell (MAFA+, GSIS)",     0.55, 7, 0.08),
]

OFF_TARGET_DEATH = 0.45   # 各段階でオフターゲット細胞が淘汰される割合

def run_protocol(start_cells=1.0e9, stages=STAGES):
    """出発細胞数から各段階を通し、(生存細胞, オンターゲット細胞) を追う"""
    on_target = start_cells   # 目的系統に乗っている細胞
    off_target = 0.0          # 逸れた細胞 (別系統・停滞)
    total_days = 0
    rows = []
    for st in stages:
        survivors = on_target * (1 - st.death_frac)
        advanced = survivors * st.yield_frac
        strayed = survivors - advanced          # 逸れた/停滞した細胞
        # オフターゲットも培養条件に適さず一部は死ぬ (選別・淘汰される)
        off_target = off_target * (1 - OFF_TARGET_DEATH) + strayed
        on_target = advanced
        total_days += st.days
        rows.append((st.name, on_target, off_target, total_days))
    return on_target, off_target, total_days, rows

beta, off, days, rows = run_protocol()
START = 1.0e9
print(f"directed differentiation from {START:.0e} pluripotent cells:")
print(f"  {'stage':<38} {'on-target':>11} {'purity':>7} {'day':>4}")
for name, on, offt, d in rows:
    purity = on / (on + offt)
    print(f"  {name:<38} {on:>11.2e} {purity:>6.0%} {d:>4}")

overall_yield = beta / START
purity = beta / (beta + off)
print(f"\noverall β-cell yield : {overall_yield:.1%} of starting cells "
      f"({days} days protocol)")
print(f"final purity         : {purity:.0%} β-cells, {1 - purity:.0%} off-target")

# ── 1回投与に必要な細胞数 / cells needed per dose ────────────────────────
# 臨床用量の目安 (架空): 体重あたり ~1.5e8 の島等価量。β細胞へ換算。
DOSE_BETA_CELLS = 5.0e8    # 1患者分に必要な機能的β細胞 (illustrative)
start_needed = DOSE_BETA_CELLS / overall_yield
print(f"\nto deliver one dose ({DOSE_BETA_CELLS:.0e} β-cells):")
print(f"  need {start_needed:.2e} starting cells → x{start_needed / DOSE_BETA_CELLS:.0f} expansion/loss factor")

# ── 段階効率の改善インパクト / where to optimize ─────────────────────────
# どの段階の歩留まりを上げると最終収率が最も伸びるか (感度分析)
print("\nsensitivity: +10%pt yield at each stage → overall yield gain:")
base = overall_yield
for i, st in enumerate(STAGES):
    boosted = [Stage(s.name, min(s.yield_frac + 0.10, 0.99) if j == i else s.yield_frac,
                     s.days, s.death_frac) for j, s in enumerate(STAGES)]
    new_yield = run_protocol(stages=boosted)[0] / START
    gain = new_yield / base - 1
    bar = "#" * int(gain * 100)
    print(f"  {st.name:<38} +{gain:>5.0%}  {bar}")
print("→ 後段 (内分泌前駆〜成熟β) の歩留まり改善が最終収率を最も押し上げる")

# ── オフターゲットの安全性 / off-target safety note ──────────────────────
print(f"""
→ 最終産物には {1 - purity:.0%} のオフターゲット細胞が含まれうる。増殖性の
  残存未分化細胞 (奇形腫リスク) の除去・選別が安全性の鍵 (純化・細胞選別)
→ 収率が低いほど 1 回投与あたりの製造コストが上がる — 後段の効率が経済性を左右する""")
