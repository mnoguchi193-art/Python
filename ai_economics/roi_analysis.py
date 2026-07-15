"""
AI 導入の投資対効果 / ROI analysis for AI adoption

NPV (正味現在価値)・回収期間・感度分析で、AI 導入プロジェクトの
投資判断を行うデモ。(数値は説明用の架空の値です / figures are illustrative)
"""

# ── プロジェクト前提 / project assumptions ────────────────────────────────
INITIAL_INVESTMENT = 500_000.0   # 導入費: 開発・統合・教育
ANNUAL_LICENSE = 120_000.0       # 年間ランニングコスト (API 利用料など)
HOURS_SAVED_PER_YEAR = 20_000.0  # 削減される作業時間
HOURLY_COST = 45.0               # 人件費単価
QUALITY_UPLIFT = 150_000.0       # 品質向上による年間増収
DISCOUNT_RATE = 0.10             # 割引率
YEARS = 5

annual_benefit = HOURS_SAVED_PER_YEAR * HOURLY_COST + QUALITY_UPLIFT
annual_net = annual_benefit - ANNUAL_LICENSE
print(f"annual benefit ${annual_benefit:,.0f} - running cost ${ANNUAL_LICENSE:,.0f} "
      f"= net ${annual_net:,.0f}/yr")

# ── NPV / net present value ──────────────────────────────────────────────
def npv(rate: float, initial: float, cashflows: list[float]) -> float:
    return -initial + sum(cf / (1 + rate) ** (t + 1) for t, cf in enumerate(cashflows))

flows = [annual_net] * YEARS
project_npv = npv(DISCOUNT_RATE, INITIAL_INVESTMENT, flows)
print(f"\nNPV over {YEARS} years @ {DISCOUNT_RATE:.0%}: ${project_npv:,.0f} "
      f"→ {'invest' if project_npv > 0 else 'reject'}")

# ── 回収期間 / payback period ────────────────────────────────────────────
cumulative = -INITIAL_INVESTMENT
for year in range(1, YEARS + 1):
    prev = cumulative
    cumulative += annual_net
    if prev < 0 <= cumulative:
        fraction = -prev / annual_net
        print(f"payback period: {year - 1 + fraction:.1f} years")
        break
else:
    print(f"payback period: not recovered within {YEARS} years")

# ── IRR を二分法で求める / internal rate of return via bisection ─────────
lo, hi = 0.0, 5.0
for _ in range(100):
    mid = (lo + hi) / 2
    if npv(mid, INITIAL_INVESTMENT, flows) > 0:
        lo = mid
    else:
        hi = mid
print(f"IRR: {(lo + hi) / 2:.1%} (vs discount rate {DISCOUNT_RATE:.0%})")

# ── 感度分析 / sensitivity analysis ──────────────────────────────────────
# どの前提が結論を最も左右するかを ±30% の振れ幅で確認する
print("\nsensitivity of NPV (each assumption ±30%):")
base_args = {
    "hours": HOURS_SAVED_PER_YEAR,
    "hourly": HOURLY_COST,
    "uplift": QUALITY_UPLIFT,
    "license": ANNUAL_LICENSE,
    "invest": INITIAL_INVESTMENT,
}

def npv_with(**over) -> float:
    a = {**base_args, **over}
    net = a["hours"] * a["hourly"] + a["uplift"] - a["license"]
    return npv(DISCOUNT_RATE, a["invest"], [net] * YEARS)

for key in base_args:
    low = npv_with(**{key: base_args[key] * 0.7})
    high = npv_with(**{key: base_args[key] * 1.3})
    swing = abs(high - low)
    print(f"  {key:<8} NPV ${min(low, high):>10,.0f} .. ${max(low, high):>10,.0f}  "
          f"(swing ${swing:,.0f})")
print("→ 削減時間と人件費単価の見積もりが投資判断を最も左右する")
