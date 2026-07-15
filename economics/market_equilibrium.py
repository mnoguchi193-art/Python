"""
Market Equilibrium (市場均衡)

Linear supply and demand:
    demand: Qd = a - b * P
    supply: Qs = c + d * P

Computes the competitive equilibrium, consumer/producer surplus,
tax incidence, and the cobweb model of price adjustment dynamics.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator


@dataclass
class LinearMarket:
    a: float  # demand intercept (quantity at P=0)
    b: float  # demand slope (>0)
    c: float  # supply intercept
    d: float  # supply slope (>0)

    def demand(self, price: float) -> float:
        return max(0.0, self.a - self.b * price)

    def supply(self, price: float) -> float:
        return max(0.0, self.c + self.d * price)

    def equilibrium(self) -> tuple[float, float]:
        """Return (price, quantity) where Qd = Qs."""
        price = (self.a - self.c) / (self.b + self.d)
        return price, self.demand(price)

    def consumer_surplus(self) -> float:
        """Area between the demand curve and the equilibrium price."""
        p_eq, q_eq = self.equilibrium()
        p_max = self.a / self.b  # choke price where demand hits zero
        return 0.5 * (p_max - p_eq) * q_eq

    def producer_surplus(self) -> float:
        """Area between the equilibrium price and the supply curve."""
        p_eq, q_eq = self.equilibrium()
        p_min = -self.c / self.d  # price where supply hits zero
        return 0.5 * (p_eq - p_min) * q_eq

    def tax_incidence(self, tax: float) -> dict[str, float]:
        """Per-unit tax on sellers: who bears the burden, and deadweight loss."""
        p0, q0 = self.equilibrium()
        # Supply shifts: Qs = c + d * (P - tax)
        taxed = LinearMarket(self.a, self.b, self.c - self.d * tax, self.d)
        p1, q1 = taxed.equilibrium()          # price paid by buyers
        return {
            "buyer_price": p1,
            "seller_price": p1 - tax,
            "buyer_burden": p1 - p0,
            "seller_burden": p0 - (p1 - tax),
            "quantity": q1,
            "tax_revenue": tax * q1,
            "deadweight_loss": 0.5 * tax * (q0 - q1),
        }

    def cobweb(self, p0: float, periods: int) -> Iterator[tuple[int, float, float]]:
        """Cobweb model: suppliers respond to last period's price.

        Yields (t, price, quantity). Converges iff d/b < 1.
        """
        p = p0
        for t in range(periods):
            q = self.supply(p)                # supply set by last price
            p = (self.a - q) / self.b         # price clears the market
            yield t, p, q

    def cobweb_converges(self) -> bool:
        return self.d / self.b < 1


if __name__ == "__main__":
    market = LinearMarket(a=100, b=2, c=-20, d=3)
    p_eq, q_eq = market.equilibrium()
    print(f"Equilibrium price    : {p_eq:.2f}")
    print(f"Equilibrium quantity : {q_eq:.2f}")
    print(f"Consumer surplus     : {market.consumer_surplus():.2f}")
    print(f"Producer surplus     : {market.producer_surplus():.2f}")

    print("\nPer-unit tax of 5 on sellers:")
    for key, value in market.tax_incidence(5).items():
        print(f"  {key:<15}: {value:.2f}")

    stable = LinearMarket(a=100, b=3, c=-20, d=2)
    print(f"\nCobweb dynamics (converges: {stable.cobweb_converges()}):")
    for t, p, q in stable.cobweb(p0=30, periods=8):
        print(f"  t={t}  P={p:6.2f}  Q={q:6.2f}")
