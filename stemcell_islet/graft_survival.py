"""
移植片の生着と生存 / Islet graft engraftment and survival

移植したβ細胞量が時間とともにどう減るかを、初期損失 (IBMIR)・自己免疫再燃・
同種拒絶の観点からモデル化し、免疫回避の3戦略 —
(1) 経門脈 + 全身免疫抑制、(2) カプセル化 (免疫抑制なし)、
(3) 遺伝子編集ハイポイミューン細胞 — を比較するデモ。

⚠ 教育目的の簡略モデル。パラメータは説明用の架空値です。
   1型糖尿病は自己免疫疾患のため、移植β細胞も自己免疫の標的になりうる点が要点。
"""

from dataclasses import dataclass

# ── 移植戦略 / transplant strategies ─────────────────────────────────────
@dataclass
class Strategy:
    name: str
    engraftment: float     # IBMIR 等を経た初期生着率 / fraction surviving engraftment
    k_autoimmune: float    # 自己免疫再燃による損失率 /month
    k_allo: float          # 同種拒絶による損失率 /month
    k_hypoxia: float       # 低酸素・線維化による損失率 /month
    is_toxicity: float     # 免疫抑制の毒性負担 (0-1, 生活の質の代理)

STRATEGIES = [
    #                        engraft  auto    allo   hypoxia  IS-tox
    Strategy("intraportal + immunosuppression", 0.50, 0.012, 0.004, 0.003, 0.35),
    Strategy("encapsulated (no immunosupp.)",   0.70, 0.002, 0.000, 0.020, 0.00),
    Strategy("hypoimmune gene-edited (no IS)",  0.75, 0.004, 0.001, 0.004, 0.00),
]

INSULIN_INDEP_THRESHOLD = 0.25   # これを上回る機能β細胞量でインスリン離脱可能

def graft_trajectory(strat, months=60, initial_mass=1.0, dt=0.25):
    """月単位で機能的β細胞量の推移を返す (initial_mass を移植)"""
    mass = initial_mass * strat.engraftment    # 生着直後
    k = strat.k_autoimmune + strat.k_allo + strat.k_hypoxia
    ts, ms = [0.0], [mass]
    t = 0.0
    while t < months:
        mass *= pow(2.718281828, -k * dt)      # 指数的損失
        t += dt
        ts.append(t)
        ms.append(mass)
    return ts, ms

def insulin_independence_months(ts, ms):
    below = next((ts[i] for i, m in enumerate(ms) if m < INSULIN_INDEP_THRESHOLD), None)
    return below

# ── 比較 / comparison ────────────────────────────────────────────────────
print("islet graft survival over 5 years (functional β-cell mass):")
print(f"  {'strategy':<34} {'engraft':>7} {'1yr':>5} {'3yr':>5} {'5yr':>5} {'indep.':>7}")
results = {}
for s in STRATEGIES:
    ts, ms = graft_trajectory(s)
    results[s.name] = (ts, ms, s)
    at = lambda yr: ms[min(range(len(ts)), key=lambda i: abs(ts[i] - yr * 12))]
    indep = insulin_independence_months(ts, ms)
    indep_str = f"{indep / 12:.1f}yr" if indep else ">5yr"
    print(f"  {s.name:<34} {s.engraftment:>6.0%} {at(1):>5.2f} {at(3):>5.2f} "
          f"{at(5):>5.2f} {indep_str:>7}")

# ── 質的トレードオフ / qualitative trade-offs ────────────────────────────
print("\ntrade-offs:")
for s in STRATEGIES:
    tox = "免疫抑制の毒性あり" if s.is_toxicity > 0 else "免疫抑制なし"
    print(f"  {s.name:<34} IS毒性 {s.is_toxicity:>3.0%}  ({tox})")

# ── 機能β細胞量の推移 / mass trajectory plot ─────────────────────────────
print("\nfunctional β-cell mass over 60 months:")
for name, (ts, ms, s) in results.items():
    step = max(1, len(ms) // 50)
    sampled = ms[::step][:50]
    hi = 0.75
    line = "".join("#" if m >= INSULIN_INDEP_THRESHOLD else "." for m in sampled)
    print(f"  {name:<34} {line}")
print(f"  {'':<34} {'(# = above insulin-independence threshold, . = below)'}")

print("""
→ 経門脈移植は生着直後に IBMIR で約半分を失い、自己免疫再燃で徐々に減る。
  免疫抑制は同種拒絶を抑えるが、自己免疫は抑えきれず毒性も伴う
→ カプセル化は免疫抑制を不要にするが、低酸素・線維化で長期生存が制限される
→ 遺伝子編集で免疫回避 (ハイポイミューン) すれば、免疫抑制なしで長期生着を狙える
  — これが「幹細胞由来 + 遺伝子編集」の組み合わせが目指す方向""")
