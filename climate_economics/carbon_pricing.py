"""
炭素価格付け / Carbon pricing: tax vs cap-and-trade

限界削減費用 (MAC) の異なる企業群に対して、炭素税と排出量取引 (キャップ &
トレード) が同じ削減量をどう達成するかを比較するデモ。
(数値は説明用の架空の値です / figures are illustrative)
"""

from dataclasses import dataclass

# ── 限界削減費用曲線 / marginal abatement cost curves ─────────────────────
# 各企業の削減費用は MAC(q) = slope × q (削減量 q に比例して高くなる)
@dataclass
class Firm:
    name: str
    emissions: float  # 現在の排出量 (万トン)
    mac_slope: float  # 限界削減費用の傾き (USD/トン per 万トン削減)

    def abatement_at(self, price: float) -> float:
        """炭素価格 price のとき、MAC = price まで削減するのが最適"""
        return min(price / self.mac_slope, self.emissions)

    def abatement_cost(self, q: float) -> float:
        return 0.5 * self.mac_slope * q * q  # MAC 曲線の下の面積

FIRMS = [
    Firm("steel",   emissions=100, mac_slope=0.8),   # 削減が安い
    Firm("cement",  emissions=80,  mac_slope=1.5),
    Firm("airline", emissions=60,  mac_slope=4.0),   # 削減が高い
]
total_emissions = sum(f.emissions for f in FIRMS)
print(f"baseline emissions: {total_emissions:.0f} (10k tons)")

# ── 炭素税 / carbon tax ──────────────────────────────────────────────────
TAX = 50.0  # USD/ton
print(f"\ncarbon tax @ ${TAX:.0f}/ton:")
tax_total = 0.0
for f in FIRMS:
    q = f.abatement_at(TAX)
    tax_total += q
    print(f"  {f.name:<8} abates {q:5.1f} (cost index {f.abatement_cost(q):>6,.0f}, "
          f"MAC at margin ${f.mac_slope * q:.0f})")
print(f"  total abatement: {tax_total:.1f} → emissions {total_emissions - tax_total:.1f}")

# ── 排出量取引 / cap-and-trade ───────────────────────────────────────────
# キャップを炭素税と同じ削減量に設定すると、許可証価格は税率に一致する
# (均衡条件: 全企業の MAC が許可証価格に等しい)
CAP = total_emissions - tax_total
# 価格 p を二分法で求める: sum(abatement_at(p)) = total - CAP
lo, hi = 0.0, 500.0
for _ in range(60):
    mid = (lo + hi) / 2
    if sum(f.abatement_at(mid) for f in FIRMS) < total_emissions - CAP:
        lo = mid
    else:
        hi = mid
permit_price = (lo + hi) / 2
print(f"\ncap-and-trade with cap = {CAP:.1f}:")
print(f"  equilibrium permit price: ${permit_price:.0f}/ton (= tax rate — equivalence)")

# ── 一律規制との比較 / uniform regulation is costlier ────────────────────
# 「全員同率削減」は MAC を均等化しないので、同じ削減量でも総費用が高い
uniform_rate = tax_total / total_emissions
uniform_cost = sum(f.abatement_cost(f.emissions * uniform_rate) for f in FIRMS)
market_cost = sum(f.abatement_cost(f.abatement_at(TAX)) for f in FIRMS)
print(f"\ntotal cost for the same abatement ({tax_total:.1f}), cost index:")
print(f"  price mechanism : {market_cost:>7,.0f} (MAC equalized across firms)")
print(f"  uniform {uniform_rate:.0%} cut : {uniform_cost:>7,.0f} "
      f"(+{uniform_cost / market_cost - 1:.0%} — cheap abaters underused)")

# ── 不確実性下の税 vs キャップ / prices vs quantities (Weitzman) ─────────
# MAC の見積もりが外れたとき: 税は「削減量」が、キャップは「価格」がぶれる
print("\nif actual MAC turns out 50% higher than expected:")
shocked = [Firm(f.name, f.emissions, f.mac_slope * 1.5) for f in FIRMS]
q_tax = sum(f.abatement_at(TAX) for f in shocked)
lo, hi = 0.0, 500.0
for _ in range(60):
    mid = (lo + hi) / 2
    if sum(f.abatement_at(mid) for f in shocked) < total_emissions - CAP:
        lo = mid
    else:
        hi = mid
print(f"  tax  : abatement {tax_total:.1f} → {q_tax:.1f} (quantity slips, price fixed)")
print(f"  cap  : permit price ${permit_price:.0f} → ${(lo + hi) / 2:.0f} (price slips, quantity fixed)")
