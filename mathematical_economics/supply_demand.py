"""
Supply & Demand — linear market equilibrium / 線形の需給均衡

Demand:  Qd = a - b * P   (b > 0)
Supply:  Qs = c + d * P   (d > 0)

Equilibrium price/quantity, consumer & producer surplus, and price elasticity.
"""

from dataclasses import dataclass


@dataclass
class LinearMarket:
    a: float  # demand intercept
    b: float  # demand slope (>0)
    c: float  # supply intercept
    d: float  # supply slope (>0)

    def demand(self, price: float) -> float:
        return self.a - self.b * price

    def supply(self, price: float) -> float:
        return self.c + self.d * price

    def equilibrium(self) -> tuple[float, float]:
        """Return (P*, Q*) where Qd == Qs."""
        if self.b + self.d == 0:
            raise ValueError("supply and demand slopes cancel out")
        price = (self.a - self.c) / (self.b + self.d)
        quantity = self.demand(price)
        return price, quantity

    def consumer_surplus(self) -> float:
        """Area between the demand curve and P* up to Q*."""
        price, quantity = self.equilibrium()
        choke = self.a / self.b  # price at which Qd == 0
        return 0.5 * (choke - price) * quantity

    def producer_surplus(self) -> float:
        """Area between P* and the supply curve up to Q*."""
        price, quantity = self.equilibrium()
        choke = -self.c / self.d  # price at which Qs == 0
        return 0.5 * (price - choke) * quantity

    def price_elasticity_of_demand(self, price: float) -> float:
        """E = (dQ/dP) * (P / Q).  Negative for a normal demand curve."""
        q = self.demand(price)
        if q == 0:
            raise ValueError("quantity is zero; elasticity undefined")
        return -self.b * price / q


if __name__ == "__main__":
    market = LinearMarket(a=100, b=2, c=10, d=3)
    p_star, q_star = market.equilibrium()
    print(f"Equilibrium: P* = {p_star:.2f}, Q* = {q_star:.2f}")
    print(f"Consumer surplus: {market.consumer_surplus():.2f}")
    print(f"Producer surplus: {market.producer_surplus():.2f}")
    print(f"Elasticity at P*: {market.price_elasticity_of_demand(p_star):.3f}")
