"""
財政移転と MPC の異質性 / Fiscal transfers with heterogeneous MPCs

給付金 (stimulus check) への消費反応が RANK と HANK でどう違うか、
また「一律給付」と「低資産層への的を絞った給付」の効果を比較するデモ。
(パラメータは説明用の架空値です / parameters are illustrative)
"""

from household import Y, mpc, simulate, solve_policy

policy = solve_policy()
cross_section = simulate(policy, n=3000, periods=500)
n = len(cross_section)

# ── 平均 MPC: HANK vs RANK ───────────────────────────────────────────────
mpcs = [mpc(policy, s, a) for a, s in cross_section]
avg_mpc = sum(mpcs) / n
RANK_MPC = 0.03  # 恒常所得仮説の代表的個人: 臨時収入の年間 MPC ≈ r
print(f"average annual MPC out of a windfall:")
print(f"  HANK (this model) : {avg_mpc:.2f}")
print(f"  RANK (rep. agent) : {RANK_MPC:.2f}")
print(f"→ 実証研究の MPC は 0.2-0.6。RANK では桁が合わず、分布を入れると近づく")
print(f"  (残りの差は非流動資産を持つ wealthy hand-to-mouth — 2資産 HANK の領分)")

# ── MPC は誰が高いか / who has high MPC? ─────────────────────────────────
order = sorted(range(n), key=lambda i: cross_section[i][0])  # 資産昇順の家計番号
quartiles = [order[i * n // 4:(i + 1) * n // 4] for i in range(4)]
print("\nMPC by wealth quartile:")
for i, q in enumerate(quartiles):
    q_mpc = sum(mpcs[j] for j in q) / len(q)
    avg_a = sum(cross_section[j][0] for j in q) / len(q)
    print(f"  Q{i + 1} (avg wealth {avg_a:>5.2f}): MPC {q_mpc:.2f} {'#' * int(q_mpc * 40)}")

# ── 一律給付 vs 的を絞った給付 / universal vs targeted transfer ───────────
# 同じ財政コスト (総額 = 0.1 × n) で、初回の消費押し上げを比較する
BUDGET_PER_HH = 0.1  # 平均所得の約10%
universal = sum(m * BUDGET_PER_HH for m in mpcs)

# 的を絞った給付: 資産下位50%に2倍額を給付 (総コストは同じ)
bottom_half = set(order[: n // 2])
targeted = sum(mpcs[j] * 2 * BUDGET_PER_HH for j in bottom_half)
print(f"\nfirst-round consumption boost (same total budget {BUDGET_PER_HH * n:,.0f}):")
print(f"  universal transfer      : {universal:>7.1f}")
print(f"  targeted to bottom 50%  : {targeted:>7.1f} (+{targeted / universal - 1:.0%})")

# ── 波及効果 / spending rounds (illustrative multiplier) ─────────────────
# 1巡目の消費は誰かの所得になり、その MPC 分がまた消費される (簡略ケインズ乗数)
print("\nspending rounds (universal transfer, income-weighted MPC):")
boost, cumulative = universal, 0.0
for round_no in range(1, 6):
    cumulative += boost
    print(f"  round {round_no}: +{boost:>6.1f} (cumulative {cumulative:>6.1f})")
    boost *= avg_mpc
print(f"  implied multiplier ≈ {cumulative / (BUDGET_PER_HH * n):.2f} "
      f"(vs RANK ≈ {1 / (1 - RANK_MPC) * RANK_MPC:.2f}... ほぼゼロ)")
print("→ 給付金政策の効果は「誰に配るか」で変わる。分布を持つモデルでしか分析できない")
