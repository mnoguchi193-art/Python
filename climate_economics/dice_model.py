"""
統合評価モデル / A toy DICE-style integrated assessment model

Nordhaus の DICE を大幅に簡略化したモデルで、経済成長 → 排出 → 気温上昇 →
経済損害のループを回し、削減政策のシナリオを比較するデモ。
(係数は雰囲気を掴むための架空値です / coefficients are illustrative)
"""

from dataclasses import dataclass, field

# ── モデル定義 / model ───────────────────────────────────────────────────
@dataclass
class World:
    gdp: float = 100.0          # 世界GDP (兆USD)
    temp: float = 1.2           # 産業革命前比の気温上昇 (°C)
    growth: float = 0.03        # 基礎成長率 (10年あたりでなく年率)
    carbon_intensity: float = 0.35  # 排出原単位 (GtCO2 / 兆USD)
    intensity_decline: float = 0.015  # 原単位の自律的低下率/年
    climate_sensitivity: float = 0.0006  # °C per GtCO2 (簡略TCRE)
    damage_coef: float = 0.006  # 損害関数の係数
    history: list = field(default_factory=list)

    def damage_fraction(self) -> float:
        """気温 T のとき GDP の何割が失われるか: D = c × T^2"""
        return self.damage_coef * self.temp**2

    def step(self, abatement: float, abatement_cost_frac: float) -> None:
        emissions = self.gdp * self.carbon_intensity * (1 - abatement)
        self.temp += self.climate_sensitivity * emissions
        gross = self.gdp * (1 + self.growth)
        net = gross * (1 - self.damage_fraction()) * (1 - abatement_cost_frac)
        self.history.append((self.gdp, self.temp, emissions, self.damage_fraction()))
        self.gdp = net
        self.carbon_intensity *= 1 - self.intensity_decline

def abatement_cost(abatement: float) -> float:
    """削減率 a のコスト (GDP比): 凸関数 — 深掘りするほど急に高くなる"""
    return 0.03 * abatement**2.6

# ── シナリオ比較 / scenario comparison ───────────────────────────────────
YEARS = 80  # 2100年頃まで
SCENARIOS = {
    "no policy":  lambda t: 0.0,
    "moderate":   lambda t: min(0.02 * t, 0.7),   # 毎年2%ptずつ削減率を強化
    "aggressive": lambda t: min(0.05 * t, 0.95),  # 急速に脱炭素
}

results = {}
for name, policy in SCENARIOS.items():
    w = World()
    for t in range(YEARS):
        a = policy(t)
        w.step(a, abatement_cost(a))
    results[name] = w

print(f"{'scenario':<12} {'GDP 2105':>10} {'temp':>7} {'damage':>8}")
for name, w in results.items():
    print(f"{name:<12} {w.gdp:>9.0f}T {w.temp:>6.2f}C {w.damage_fraction():>7.1%}")

# ── 軌跡の表示 / trajectories ────────────────────────────────────────────
print("\ntemperature paths (each row = 20 years):")
for name, w in results.items():
    temps = [w.history[t][1] for t in range(0, YEARS, 20)] + [w.temp]
    path = " → ".join(f"{x:.1f}" for x in temps)
    print(f"  {name:<12} {path} °C")

# ── 「今払うか後で払うか」/ mitigation cost vs avoided damage ─────────────
base = results["no policy"]
for name in ("moderate", "aggressive"):
    w = results[name]
    gdp_gain = w.gdp - base.gdp
    print(f"\n{name}: GDP in 2105 vs no-policy: {gdp_gain:+,.0f}T "
          f"({'policy pays for itself' if gdp_gain > 0 else 'costs exceed avoided damage by 2105'})")
print("→ 削減費用は前半に、回避される損害は後半に効く。評価期間と割引率が結論を決める")
