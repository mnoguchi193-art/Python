"""
Inference Engine (推論エンジン / 記号的推論)

「知っている事実からまだ知らない結論を導く」記号的 AI の古典手法。
知識をルール (IF-THEN) として表現し、論理的に推論する。

- 前向き推論 (forward chaining): 事実からルールを次々適用し、
  導ける結論をすべて導出する (データ駆動)
- 後ろ向き推論 (backward chaining): 証明したい目標から遡り、
  それを支える事実があるか確認する (ゴール駆動)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, List, Set


@dataclass(frozen=True)
class Rule:
    """IF conditions THEN conclusion 形式のルール。"""
    conditions: FrozenSet[str]
    conclusion: str

    def __str__(self) -> str:
        return f"IF {' AND '.join(sorted(self.conditions))} THEN {self.conclusion}"


class InferenceEngine:
    def __init__(self, rules: List[Rule]):
        self.rules = rules

    def forward_chain(self, facts: Set[str], verbose: bool = False) -> Set[str]:
        """前向き推論: 新しい事実が増えなくなるまでルールを適用。"""
        known = set(facts)
        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                if rule.conditions <= known and rule.conclusion not in known:
                    known.add(rule.conclusion)
                    changed = True
                    if verbose:
                        print(f"  適用: {rule}")
        return known

    def backward_chain(self, goal: str, facts: Set[str],
                       _visiting: Set[str] = None) -> bool:
        """後ろ向き推論: goal が事実から証明できるか再帰的に確認。"""
        if goal in facts:
            return True
        visiting = _visiting or set()
        if goal in visiting:  # 循環ルールによる無限再帰を防ぐ
            return False
        for rule in self.rules:
            if rule.conclusion == goal:
                if all(
                    self.backward_chain(cond, facts, visiting | {goal})
                    for cond in rule.conditions
                ):
                    return True
        return False


if __name__ == "__main__":
    # 動物分類の知識ベース
    rules = [
        Rule(frozenset({"毛がある"}), "哺乳類である"),
        Rule(frozenset({"母乳で育てる"}), "哺乳類である"),
        Rule(frozenset({"羽がある"}), "鳥類である"),
        Rule(frozenset({"哺乳類である", "肉を食べる"}), "肉食獣である"),
        Rule(frozenset({"肉食獣である", "縞模様がある"}), "トラである"),
        Rule(frozenset({"肉食獣である", "たてがみがある"}), "ライオンである"),
        Rule(frozenset({"鳥類である", "飛べない", "泳げる"}), "ペンギンである"),
    ]
    engine = InferenceEngine(rules)

    print("=== 前向き推論 (forward chaining) ===")
    observed = {"毛がある", "肉を食べる", "縞模様がある"}
    print("観測した事実:", observed)
    conclusions = engine.forward_chain(observed, verbose=True)
    print("導かれた結論:", conclusions - observed)

    print("\n=== 後ろ向き推論 (backward chaining) ===")
    facts = {"羽がある", "飛べない", "泳げる"}
    print("事実:", facts)
    for goal in ["ペンギンである", "トラである"]:
        result = engine.backward_chain(goal, facts)
        print(f"「{goal}」は証明できるか? -> {result}")
