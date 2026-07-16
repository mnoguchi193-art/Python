"""
ホモキラリティ / Homochirality: spontaneous chiral symmetry breaking (Frank)

生命はなぜ片方の掌性 (L型アミノ酸・D型糖) だけを使うのか。Frank (1953) の
モデルで、L・R 両鏡像体が (1) それぞれ自己触媒的に増え、(2) 互いに打ち消し合う
(相互拮抗) とき、対称な racemic 状態が不安定になり、微小な揺らぎが増幅されて
片方の鏡像体だけが残る (自発的対称性の破れ) 過程を示すデモ。

⚠ 教育目的の簡略モデルです。
"""

from kinetics import integrate

# ── Frank モデル / Frank's model ─────────────────────────────────────────
# dl/dt = l·(1 − l − r) − g·l·r   (自己触媒成長 − 相互拮抗)
# dr/dt = r·(1 − l − r) − g·l·r
#   g > 0 の相互拮抗があると、対称点 l=r が不安定になる。
def make_deriv(g):
    def deriv(state, t):
        l, r = state
        common = 1 - l - r
        return [l * common - g * l * r, r * common - g * l * r]
    return deriv

def ee(l, r):
    """鏡像体過剰率 (enantiomeric excess) = (L−R)/(L+R)"""
    return (l - r) / (l + r) if (l + r) > 0 else 0.0

# ── 相互拮抗の有無で比較 / with vs without mutual antagonism ─────────────
L0, R0 = 0.010, 0.010  # ほぼ対称な初期条件
BIAS = 0.00002          # ごく僅かな初期の揺らぎ (ee ≈ 0.1% 相当)

print("chiral symmetry breaking from a tiny initial fluctuation (ee ≈ 0.1%):")
print(f"  {'time':>5} | {'no antagonism (g=0)':>22} | {'antagonism (g=2)':>20}")
print(f"  {'':>5} | {'L':>7}{'R':>7}{'ee':>7} | {'L':>7}{'R':>7}{'ee':>5}")
ts0, ys0 = integrate(make_deriv(0.0), [L0 + BIAS, R0], 0, 60, 0.05)
ts2, ys2 = integrate(make_deriv(2.0), [L0 + BIAS, R0], 0, 60, 0.05)
def at(ts, ys, t):
    i = min(range(len(ts)), key=lambda k: abs(ts[k] - t))
    return ys[i]
for t in (0, 10, 20, 30, 45, 60):
    l0, r0 = at(ts0, ys0, t)
    l2, r2 = at(ts2, ys2, t)
    print(f"  {t:>5} | {l0:>7.3f}{r0:>7.3f}{ee(l0, r0):>6.0%} "
          f"| {l2:>7.3f}{r2:>7.3f}{ee(l2, r2):>5.0%}")
print("→ 拮抗なし (g=0): 両鏡像体が等しく増え、racemic (ee≈0) のまま — 対称性は保たれる")
print("→ 拮抗あり (g=2): 微小な差が増幅され、片方 (L) だけが残る (ee→100%) — 対称性の破れ")

# ── 初期の揺らぎの向きが結果を決める / the fluctuation sets the outcome ──
print("\nthe sign of the initial fluctuation decides which handedness wins:")
for bias, label in [(+BIAS, "L slightly favored"), (-BIAS, "R slightly favored"),
                    (0.0, "perfectly symmetric")]:
    ts, ys = integrate(make_deriv(2.0), [L0 + max(bias, 0), R0 + max(-bias, 0)], 0, 80, 0.05)
    lf, rf = ys[-1]
    outcome = ("L-world" if ee(lf, rf) > 0.5 else "R-world" if ee(lf, rf) < -0.5
               else "racemic (unresolved)")
    print(f"  {label:<22} → final ee {ee(lf, rf):>+5.0%}  ({outcome})")

# ── ee の増幅 / amplification of enantiomeric excess ─────────────────────
print("\nee amplification over time (g=2), tiny 0.1% seed → homochirality:")
spark = "".join("█" if ee(l, r) > 0.8 else ("▄" if ee(l, r) > 0.3 else "·")
                for l, r in ys2[::max(1, len(ys2) // 50)])
print(f"  |{spark}| final ee {ee(*ys2[-1]):.0%}")

print("""
→ 自己触媒 + 相互拮抗があれば、対称な状態は不安定 — 必ずどちらかに倒れる
→ 倒れる向きは初期のランダムな揺らぎが決める (原理的には L/R 五分五分)
→ 生命が片方の掌性だけを使うのは、こうした対称性の破れの帰結かもしれない
→ (なぜ地球の生命が特定の向きなのかは、偶然か・別の要因かなお未解決の問い)""")
