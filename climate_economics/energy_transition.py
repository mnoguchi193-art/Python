"""
エネルギー転換の経済学 / Economics of the energy transition

学習曲線 (Wright の法則) による再エネのコスト低下、グリッドパリティ到達、
座礁資産のリスクをシミュレートするデモ。
(数値は説明用の架空の値です / figures are illustrative)
"""

import math

# ── Wright の法則 / learning curves ──────────────────────────────────────
# 累積生産量が2倍になるたびにコストが一定率 (learning rate) 下がる
def wright_cost(initial_cost: float, initial_capacity: float,
                capacity: float, learning_rate: float) -> float:
    doublings = math.log2(capacity / initial_capacity)
    return initial_cost * (1 - learning_rate) ** doublings

SOLAR_LR, WIND_LR, COAL_LR = 0.20, 0.12, 0.0  # 成熟技術は学習がほぼ止まる
solar0, wind0, coal = 120.0, 90.0, 75.0       # 発電単価 (USD/MWh)
solar_cap0, wind_cap0 = 100.0, 200.0          # 累積導入量 (GW)

print(f"{'year':>5} {'solar GW':>9} {'solar':>7} {'wind':>7} {'coal':>7}  (USD/MWh)")
solar_cap, wind_cap = solar_cap0, wind_cap0
parity_year = None
for year in range(2025, 2046, 5):
    s = wright_cost(solar0, solar_cap0, solar_cap, SOLAR_LR)
    w = wright_cost(wind0, wind_cap0, wind_cap, WIND_LR)
    print(f"{year:>5} {solar_cap:>9,.0f} {s:>7.1f} {w:>7.1f} {coal:>7.1f}")
    if parity_year is None and s < coal:
        parity_year = year
    solar_cap *= 1.25 ** 5  # 年25%成長
    wind_cap *= 1.10 ** 5
print(f"→ grid parity for solar around {parity_year} (learning rate {SOLAR_LR:.0%}/doubling)")

# ── 導入が学習を生み、学習が導入を生む / deployment-learning feedback ──────
# 補助金で初期導入を押し上げると、パリティ到達が早まり総費用が下がることがある
def years_to_parity(annual_growth: float) -> tuple[int, float]:
    cap, subsidy_total = solar_cap0, 0.0
    for year in range(60):
        cost = wright_cost(solar0, solar_cap0, cap, SOLAR_LR)
        if cost <= coal:
            return year, subsidy_total
        # パリティまでの差額を補助金で埋めると仮定 (年間発電量: 1GW≈2TWh)
        subsidy_total += (cost - coal) * cap * 2_000 / 1e6  # 百万USD→兆換算は略
        cap *= 1 + annual_growth
    return 60, subsidy_total

print("\nsubsidized deployment growth vs cumulative subsidy until parity:")
for g in (0.10, 0.20, 0.30):
    yrs, subsidy = years_to_parity(g)
    print(f"  {g:.0%}/yr growth → parity in {yrs:>2} years, "
          f"cumulative subsidy index {subsidy:>7,.0f}")
print("→ 速い導入は補助総額を増やすとは限らない (学習が単価差を先に潰すため)")

# ── 座礁資産 / stranded assets ───────────────────────────────────────────
# 石炭火力の新設は40年稼働が前提。パリティ後は市場価格で回収できなくなる
PLANT_LIFE, PLANT_CAPEX = 40, 2_000.0  # 百万USD/GW
build_year = 2025
annual_margin_before = 60.0  # パリティ前の年間粗利 (百万USD/GW)
annual_margin_after = 5.0    # パリティ後 (稼働率低下・価格下落)

parity = parity_year or 2040
value = 0.0
for y in range(build_year, build_year + PLANT_LIFE):
    margin = annual_margin_before if y < parity else annual_margin_after
    value += margin / 1.06 ** (y - build_year)
print(f"\ncoal plant built {build_year} (capex {PLANT_CAPEX:,.0f}):")
print(f"  PV of lifetime margins: {value:,.0f} → "
      f"{'viable' if value > PLANT_CAPEX else f'stranded (recovers {value / PLANT_CAPEX:.0%} of capex)'}")
print("→ 技術のコスト曲線を読み違えると、インフラ投資が座礁資産になる")
