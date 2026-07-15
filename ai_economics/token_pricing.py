"""
LLM API の価格モデル / LLM API pricing economics

トークン単価・キャッシュ割引・バッチ割引から API 利用コストを試算し、
セルフホスティングとの損益分岐点を求めるデモ。
(価格は説明用の架空の値です / prices below are illustrative, not real)
"""

from dataclasses import dataclass

# ── トークン単価モデル / per-token pricing ────────────────────────────────
@dataclass(frozen=True)
class ModelPrice:
    name: str
    input_per_mtok: float   # USD per 1M input tokens
    output_per_mtok: float  # USD per 1M output tokens
    cached_input_per_mtok: float  # USD per 1M cached input tokens

    def cost(self, input_tok: int, output_tok: int, cached_tok: int = 0) -> float:
        fresh = max(input_tok - cached_tok, 0)
        return (
            fresh * self.input_per_mtok
            + cached_tok * self.cached_input_per_mtok
            + output_tok * self.output_per_mtok
        ) / 1_000_000

SMALL = ModelPrice("small", input_per_mtok=0.25, output_per_mtok=1.25, cached_input_per_mtok=0.03)
LARGE = ModelPrice("large", input_per_mtok=3.00, output_per_mtok=15.00, cached_input_per_mtok=0.30)

# 1リクエストあたり: システムプロンプト 2k tok (キャッシュ可) + 質問 500 tok + 回答 800 tok
SYSTEM_TOK, QUESTION_TOK, ANSWER_TOK = 2_000, 500, 800
REQUESTS_PER_DAY = 10_000

for model in (SMALL, LARGE):
    no_cache = model.cost(SYSTEM_TOK + QUESTION_TOK, ANSWER_TOK)
    with_cache = model.cost(SYSTEM_TOK + QUESTION_TOK, ANSWER_TOK, cached_tok=SYSTEM_TOK)
    print(f"{model.name}: per request ${no_cache:.5f} → with prompt cache ${with_cache:.5f} "
          f"({(1 - with_cache / no_cache):.0%} saved)")
    print(f"  monthly ({REQUESTS_PER_DAY:,} req/day): "
          f"${no_cache * REQUESTS_PER_DAY * 30:,.0f} → ${with_cache * REQUESTS_PER_DAY * 30:,.0f}")

# ── バッチ処理割引 / batch discount ──────────────────────────────────────
BATCH_DISCOUNT = 0.5  # 50% off for async batch processing
realtime = LARGE.cost(SYSTEM_TOK + QUESTION_TOK, ANSWER_TOK) * REQUESTS_PER_DAY * 30
batch = realtime * BATCH_DISCOUNT
print(f"\nbatch processing: ${realtime:,.0f}/mo → ${batch:,.0f}/mo (latency vs cost trade-off)")

# ── セルフホスト損益分岐点 / self-hosting break-even ─────────────────────
GPU_MONTHLY = 2_500.0        # GPU サーバー月額 (fixed cost)
SELF_HOST_PER_REQ = 0.0002   # 電力・運用の変動費 (variable cost)

api_per_req = LARGE.cost(SYSTEM_TOK + QUESTION_TOK, ANSWER_TOK, cached_tok=SYSTEM_TOK)
# GPU_MONTHLY + SELF_HOST_PER_REQ * n = api_per_req * n を n について解く
break_even = GPU_MONTHLY / (api_per_req - SELF_HOST_PER_REQ)
print(f"\nself-hosting break-even: {break_even:,.0f} requests/month")
print(f"  (below → API is cheaper, above → self-hosting is cheaper)")

for monthly_req in (100_000, 500_000, 2_000_000):
    api_cost = api_per_req * monthly_req
    self_cost = GPU_MONTHLY + SELF_HOST_PER_REQ * monthly_req
    winner = "API" if api_cost < self_cost else "self-host"
    print(f"  {monthly_req:>9,} req/mo: API ${api_cost:>8,.0f} vs self ${self_cost:>8,.0f} → {winner}")
