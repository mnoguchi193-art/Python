"""
AI と労働市場 / AI automation and the labor market

タスクベースモデル (Acemoglu & Restrepo 風の簡略版) で、AI による
自動化が賃金・雇用・生産量に与える影響をシミュレートするデモ。
(パラメータは説明用の架空の値です / parameters are illustrative)
"""

from dataclasses import dataclass

# ── タスクベース生産モデル / task-based production ────────────────────────
# 生産は多数のタスクから成る。各タスクは人間か AI のどちらか安い方が担う。
@dataclass
class Task:
    name: str
    human_cost: float  # 人間がこのタスクを1単位こなすコスト
    ai_cost: float | None  # AI で自動化した場合のコスト (None = 自動化不能)

    def performer(self) -> str:
        if self.ai_cost is not None and self.ai_cost < self.human_cost:
            return "AI"
        return "human"

TASKS = [
    Task("data entry",        human_cost=15.0, ai_cost=0.5),
    Task("translation",       human_cost=40.0, ai_cost=2.0),
    Task("code review",       human_cost=60.0, ai_cost=8.0),
    Task("customer support",  human_cost=25.0, ai_cost=6.0),
    Task("sales negotiation", human_cost=80.0, ai_cost=None),
    Task("nursing care",      human_cost=30.0, ai_cost=None),
    Task("strategic planning", human_cost=120.0, ai_cost=None),
]

automated = [t for t in TASKS if t.performer() == "AI"]
print(f"automated tasks: {len(automated)}/{len(TASKS)}")
for t in TASKS:
    saving = f"(saves {1 - t.ai_cost / t.human_cost:.0%})" if t.performer() == "AI" else ""
    print(f"  {t.name:<18} → {t.performer():<6} {saving}")

# ── 置換効果 vs 生産性効果 / displacement vs productivity effect ─────────
# 自動化は既存の仕事を奪う (置換効果) が、コスト低下で需要が増え、
# 自動化できないタスクの雇用を増やす (生産性効果) こともある。
old_unit_cost = sum(t.human_cost for t in TASKS)
new_unit_cost = sum(t.ai_cost if t.performer() == "AI" else t.human_cost for t in TASKS)
print(f"\nunit cost: {old_unit_cost:.0f} → {new_unit_cost:.0f} "
      f"({1 - new_unit_cost / old_unit_cost:.0%} cheaper)")

# 需要の価格弾力性: 価格が1%下がると需要が elasticity % 増える
ELASTICITY = 1.8
demand_growth = (old_unit_cost / new_unit_cost) ** ELASTICITY
print(f"output demand: ×{demand_growth:.2f} (price elasticity = {ELASTICITY})")

# 人間の仕事量 = 人間担当タスク数 × 生産量
human_tasks_before = len(TASKS)
human_tasks_after = len(TASKS) - len(automated)
labor_before = human_tasks_before * 1.0
labor_after = human_tasks_after * demand_growth
print(f"human labor demand: {labor_before:.1f} → {labor_after:.1f} "
      f"({'net gain' if labor_after > labor_before else 'net loss'})")

# ── 弾力性による分岐 / the race between the two effects ──────────────────
print("\nnet employment effect by demand elasticity:")
for e in (0.5, 1.0, 1.5, 2.0, 3.0):
    growth = (old_unit_cost / new_unit_cost) ** e
    after = human_tasks_after * growth
    bar = "#" * int(after * 4)
    print(f"  elasticity {e:.1f}: labor {after:5.2f}  {bar}")
print("→ 需要が弾力的なほど生産性効果が勝ち、雇用は増えやすい")
