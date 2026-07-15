"""
炭素の社会的費用と割引 / Social cost of carbon and discounting

今日の1トンの CO2 排出が将来にわたって与える損害の現在価値 (SCC) を計算し、
割引率の選び方 (Ramsey 則) が結論をどれほど左右するかを見るデモ。
(数値は説明用の架空の値です / figures are illustrative)
"""

# ── 1トンの排出が生む損害の流列 / damage stream from 1 ton of CO2 ─────────
# 排出された CO2 は大気中に長く残り、毎年少しずつ損害を与える。
# 損害は経済成長とともに増えるが、CO2 は徐々に吸収されて減衰する。
HORIZON = 300           # 評価年数
DAMAGE_YEAR_ONE = 0.15  # 初年度の損害 (USD/ton/year)
ECON_GROWTH = 0.02      # 損害は経済規模に比例して成長
DECAY = 0.005           # 大気中 CO2 の吸収による減衰率/年

def damage_stream() -> list[float]:
    return [
        DAMAGE_YEAR_ONE * (1 + ECON_GROWTH) ** t * (1 - DECAY) ** t
        for t in range(HORIZON)
    ]

def scc(discount_rate: float) -> float:
    return sum(d / (1 + discount_rate) ** t for t, d in enumerate(damage_stream()))

# ── 割引率で SCC はどう変わるか / SCC vs discount rate ────────────────────
print("social cost of carbon by discount rate:")
for r in (0.07, 0.05, 0.03, 0.025, 0.021):
    print(f"  r = {r:.1%} → SCC = ${scc(r):>7.0f}/ton")
print("→ 割引率を半分にすると SCC は数倍になる。炭素価格論争の核心は倫理 (割引率) にある")

# ── Ramsey 則 / the Ramsey rule ──────────────────────────────────────────
# r = ρ + η × g
#   ρ: 純粋時間選好率 (将来世代を割り引く倫理的パラメータ)
#   η: 消費の限界効用弾力性 (豊かな世代への追加1ドルの価値の減り方)
#   g: 一人あたり消費成長率
print("\nRamsey rule r = ρ + η×g (g = 2%):")
G = 0.02
CASES = [
    ("Stern (2006)",     0.001, 1.0),  # 将来世代をほぼ割り引かない
    ("Nordhaus (2008)",  0.015, 2.0),  # 市場利子率に整合させる
    ("high impatience",  0.030, 2.0),
]
for label, rho, eta in CASES:
    r = rho + eta * G
    print(f"  {label:<16} ρ={rho:.1%}, η={eta:.1f} → r={r:.1%} → SCC ${scc(r):>6.0f}/ton")

# ── 世代間の重みを見る / how much does year-100 damage count? ─────────────
print("\npresent value of $100 damage occurring in year N:")
print(f"  {'N':>4} {'r=1.4% (Stern)':>16} {'r=5.5%':>10}")
for n in (10, 50, 100, 200):
    lo_r = 100 / 1.014**n
    hi_r = 100 / 1.055**n
    print(f"  {n:>4} {lo_r:>15.2f}$ {hi_r:>9.4f}$")
print("→ 高割引率では100年後の損害はほぼゼロ扱い。SCC の差は数式でなく世界観の差")

# ── 炭素税への含意 / implication for the carbon tax level ────────────────
EMISSIONS_PER_CAR_YEAR = 4.6  # 平均的な自家用車の年間排出 (ton)
print("\nannual climate cost of one average car:")
for label, rho, eta in CASES:
    r = rho + eta * G
    print(f"  {label:<16} ${scc(r) * EMISSIONS_PER_CAR_YEAR:>7.0f}/year")
