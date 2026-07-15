"""
金融政策の伝達経路 / Monetary transmission: direct vs indirect effects

1期限りの利下げが消費を増やす経路を Kaplan-Moll-Violante (2018) 流に分解:
  直接効果 = 金利変化への異時点間代替 (借入制約下の家計は反応できない)
  間接効果 = 景気改善による労働所得増への反応 (MPC が効く)
RANK では直接効果がほぼすべて。HANK では高MPC家計の存在が間接効果を生む。
(パラメータは説明用の架空値です / parameters are illustrative)
"""

from household import (A_GRID, BETA, P, R, Y, consumption, interp, mpc,
                       simulate, solve_policy)

# ── 1期限りの利下げへの反応 / policy under a transitory rate cut ──────────
# 来期以降はベースラインに戻るので、Euler 方程式の右辺 (来期の消費政策) は
# 据え置き、今期の異時点間価格 β(1+r) だけを変えて1ステップ逆算する。
def transitory_policy(base: list[list[float]], r_now: float) -> list[list[float]]:
    n_s = len(Y)
    out = []
    for s in range(n_s):
        a_end, c_end = [], []
        for j, a_next in enumerate(A_GRID):
            emu = sum(P[s][sp] / base[sp][j] for sp in range(n_s))
            ce = 1.0 / (BETA * (1 + r_now) * emu)
            a_end.append((ce + a_next - Y[s]) / (1 + R))  # 今期の予算は既存資産の利回りのまま
            c_end.append(ce)
        out.append([
            (1 + R) * a + Y[s] if a <= a_end[0] else interp(a_end, c_end, a)
            for a in A_GRID
        ])
    return out

policy = solve_policy(r=R)
cross_section = simulate(policy, n=3000, periods=500)
n = len(cross_section)
base_c = sum(consumption(policy, s, a) for a, s in cross_section)

# ── 分解 / decomposition ─────────────────────────────────────────────────
RATE_CUT = 0.005     # 0.5%pt の利下げ (1期のみ)
INCOME_BOOST = 0.01  # 一般均衡での労働所得の増加 (簡略化のため外生で与える)

policy_cut = transitory_policy(policy, R - RATE_CUT)
direct_i = [
    consumption(policy_cut, s, a) - consumption(policy, s, a)
    for a, s in cross_section
]
indirect_i = [mpc(policy, s, a) * Y[s] * INCOME_BOOST for a, s in cross_section]

direct, indirect = sum(direct_i), sum(indirect_i)
total = direct + indirect
print(f"consumption response to a {RATE_CUT:.1%} transitory rate cut "
      f"(GE income +{INCOME_BOOST:.0%}):")
print(f"  direct  (intertemporal substitution) : {direct:>6.2f} ({direct / total:.0%})")
print(f"  indirect (labor income x MPC)        : {indirect:>6.2f} ({indirect / total:.0%})")
print(f"  total : {total:.2f} ({total / base_c:.2%} of aggregate consumption)")

# ── RANK との比較 / the RANK benchmark ───────────────────────────────────
# 代表的個人は借入制約から遠く MPC ≈ 0.03。間接効果はほぼ消える
rank_direct = RATE_CUT / (1 + R) * base_c  # log効用: Δc/c ≈ Δr/(1+r)
rank_indirect = 0.03 * sum(Y[s] for _, s in cross_section) * INCOME_BOOST
print(f"\nRANK benchmark: direct {rank_direct / (rank_direct + rank_indirect):.0%}, "
      f"indirect {rank_indirect / (rank_direct + rank_indirect):.0%}")

# ── 誰がどの経路で反応するか / channels across the distribution ───────────
order = sorted(range(n), key=lambda i: cross_section[i][0])
print("\nby wealth quartile (Q1 = poorest):")
print(f"  {'':<4} {'direct':>7} {'indirect':>9} {'indirect share':>15}")
for q in range(4):
    idx = order[q * n // 4:(q + 1) * n // 4]
    d = sum(direct_i[i] for i in idx)
    ind = sum(indirect_i[i] for i in idx)
    print(f"  Q{q + 1:<3} {d:>7.2f} {ind:>9.2f} {ind / (d + ind):>14.0%}")

print("""
→ 借入制約付近の家計は金利に反応できず、所得経由 (間接効果) でのみ動く
→ フルの KMV モデルでは非流動資産により hand-to-mouth が約3割に達し、
  間接効果が過半を占める — 「金融政策は所得経路で効く」が HANK の中心命題
→ 政策含意: 利下げの効きは労働市場の反応 (賃金・雇用) と財政に依存する""")
