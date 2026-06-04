"""
Consumer theory — Cobb-Douglas utility maximization / 消費者理論

Maximize  U(x, y) = x**alpha * y**beta
subject to  px * x + py * y = income.

The interior optimum spends a constant income share on each good:
    x* = (alpha / (alpha + beta)) * income / px
    y* = (beta  / (alpha + beta)) * income / py
"""

from dataclasses import dataclass


@dataclass
class CobbDouglasConsumer:
    alpha: float
    beta: float

    def utility(self, x: float, y: float) -> float:
        return x**self.alpha * y**self.beta

    def marginal_rate_of_substitution(self, x: float, y: float) -> float:
        """MRS = MUx / MUy = (alpha / beta) * (y / x)."""
        if x == 0:
            raise ValueError("MRS undefined at x = 0")
        return (self.alpha / self.beta) * (y / x)

    def optimal_bundle(
        self, income: float, px: float, py: float
    ) -> tuple[float, float]:
        share = self.alpha + self.beta
        x = (self.alpha / share) * income / px
        y = (self.beta / share) * income / py
        return x, y

    def demand_x(self, income: float, px: float) -> float:
        """Marshallian demand for good x (independent of py here)."""
        share = self.alpha + self.beta
        return (self.alpha / share) * income / px


if __name__ == "__main__":
    consumer = CobbDouglasConsumer(alpha=0.5, beta=0.5)
    income, px, py = 100.0, 2.0, 5.0
    x, y = consumer.optimal_bundle(income, px, py)
    print(f"Optimal bundle: x* = {x:.2f}, y* = {y:.2f}")
    print(f"Utility at optimum: {consumer.utility(x, y):.3f}")
    print(f"MRS at optimum: {consumer.marginal_rate_of_substitution(x, y):.3f}")
    print(f"Price ratio px/py: {px / py:.3f}  (equals MRS at the optimum)")
