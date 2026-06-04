"""
Production — Cobb-Douglas production function / 生産関数

Y = A * K**alpha * L**beta

Marginal products, output elasticities, and returns to scale.
"""

from dataclasses import dataclass


@dataclass
class CobbDouglasProduction:
    A: float      # total factor productivity
    alpha: float  # output elasticity of capital
    beta: float   # output elasticity of labor

    def output(self, capital: float, labor: float) -> float:
        return self.A * capital**self.alpha * labor**self.beta

    def marginal_product_capital(self, capital: float, labor: float) -> float:
        """MPK = alpha * Y / K."""
        return self.alpha * self.output(capital, labor) / capital

    def marginal_product_labor(self, capital: float, labor: float) -> float:
        """MPL = beta * Y / L."""
        return self.beta * self.output(capital, labor) / labor

    def returns_to_scale(self) -> str:
        total = self.alpha + self.beta
        if total > 1:
            return "increasing"
        if total < 1:
            return "decreasing"
        return "constant"


if __name__ == "__main__":
    firm = CobbDouglasProduction(A=1.0, alpha=0.3, beta=0.7)
    K, L = 100.0, 50.0
    print(f"Output Y: {firm.output(K, L):.2f}")
    print(f"MPK: {firm.marginal_product_capital(K, L):.4f}")
    print(f"MPL: {firm.marginal_product_labor(K, L):.4f}")
    print(f"Returns to scale: {firm.returns_to_scale()}")

    # Doubling both inputs under constant returns doubles output.
    print(f"Y(2K, 2L) / Y(K, L): {firm.output(2 * K, 2 * L) / firm.output(K, L):.3f}")
