"""
B細胞のリセット / B-cell depletion and repertoire reset

抗 CD19 CAR-T が CD19+ B細胞を枯渇させる一方、CD19- の長寿命形質細胞は
温存される (=ワクチン抗体は保たれる) こと、B細胞無形成 → 再構築の時間経過、
そして再生した「初期化された」レパートリーで自己反応性が下がることを示すデモ。

⚠ 教育目的の簡略モデル。パラメータは説明用の架空値です。
   参考にした臨床像: Mackensen et al. Nat Med 2022 / Müller et al. NEJM 2024
"""

from cell_kinetics import rk4_step

# ── コンパートメント / compartments ──────────────────────────────────────
# 状態 = [C, M, N, Pa, Pp, Ab_auto, Ab_prot]
#   C, M    : CAR-T エフェクター / メモリー
#   N       : ナイーブ・成熟 CD19+ B細胞 (CAR-T の標的)
#   Pa      : 自己反応性の短命形質芽細胞 (CD19+, 標的)   → 自己抗体を産生
#   Pp      : 保護的な長寿命形質細胞 (CD19-, 温存される)  → 保護抗体を産生
#   Ab_auto : 自己抗体価 (例: 抗dsDNA)
#   Ab_prot : 保護抗体価 (例: ワクチン由来)
#   X       : CAR-T の疲弊 (exhaustion) — 増殖に伴い蓄積し、増殖を抑える
P = dict(
    rho=1.75, delta_c=0.25, mu=0.10, alpha=0.30, delta_m=0.04, Kb=90.0,
    eps=0.009,        # 増殖に伴う疲弊の蓄積速度 / exhaustion accrual per division
    sigma=6.0,        # 骨髄からのナイーブB供給 / marrow output of naive B
    delta_n=0.05,     # ナイーブBの自然死 / naive B turnover
    kappa=0.080,      # CAR-T による CD19+ 殺傷 / CD19+ killing
    birth_a=0.04,     # ナイーブ→自己反応性形質芽細胞 / autoreactive differentiation
    delta_pa=0.20,    # 自己反応性形質芽細胞は短命 / short-lived
    delta_pp=0.0008,  # 保護的形質細胞は非常に長寿命 / very long-lived
    prod_a=1.0, prod_p=1.0,   # 抗体産生率 / antibody production
    decay_ab=0.05,    # 抗体の半減 / antibody decay
)

def deriv(state, t, p=P, birth_a=None):
    C, M, N, Pa, Pp, Aa, Ap, X = state
    birth_a = p["birth_a"] if birth_a is None else birth_a
    target = N + Pa                       # CD19+ の総抗原量
    signal = target / (target + p["Kb"])
    prolif = p["rho"] * signal * C / (1 + X)   # 疲弊が増殖を抑える
    dC = (prolif + p["alpha"] * signal * M / (1 + X)
          - p["mu"] * (1 - signal) * C - p["delta_c"] * C)
    dM = p["mu"] * (1 - signal) * C - p["alpha"] * signal * M / (1 + X) - p["delta_m"] * M
    dX = p["eps"] * signal * (C + M)      # 抗原刺激を受けるほど疲弊が進む (不可逆)
    kill = p["kappa"] * C
    dN = p["sigma"] - p["delta_n"] * N - kill * N          # 供給 − 死 − CAR-T殺傷
    dPa = birth_a * N - p["delta_pa"] * Pa - kill * Pa      # CD19+ なので殺傷される
    dPp = -p["delta_pp"] * Pp                               # CD19-: CAR-T の影響なし
    dAa = p["prod_a"] * Pa - p["decay_ab"] * Aa
    dAp = p["prod_p"] * Pp - p["decay_ab"] * Ap
    return [dC, dM, dN, dPa, dPp, dAa, dAp, dX]

# ── 初期状態 / initial (pre-treatment) steady state ──────────────────────
N0 = P["sigma"] / P["delta_n"]                 # = 120 ナイーブB
Pa0 = P["birth_a"] * N0 / P["delta_pa"]        # 自己反応性形質芽細胞
Pp0 = 30.0                                     # 保護的形質細胞 (蓄積済み)
Aa0 = P["prod_a"] * Pa0 / P["decay_ab"]        # 自己抗体
Ap0 = P["prod_p"] * Pp0 / P["decay_ab"]        # 保護抗体

def simulate(days=400, dt=0.05, reset_day=150, reset_factor=0.25):
    """CAR-T 投与後の全コンパートメントを積分して (times, states) を返す。

    CAR-T は抗原に駆動され増殖するが、疲弊 X が蓄積して増殖が止まり収縮する
    (製造された細胞の有限な増殖能)。自己再生する B 細胞では CAR-T は再拡大せず、
    一過性に留まる — これが自己免疫応用で B 細胞が数ヶ月で戻る理由。
    reset_factor を 1.0 にすると「リセットなし」= B 細胞が戻ると再燃するケース。
    """
    state0 = [1.0, 0.0, N0, Pa0, Pp0, Aa0, Ap0, 0.0]   # CAR-T 1 単位投与、疲弊 X=0
    ts, ys = [0.0], [state0]
    state, t = state0, 0.0
    for _ in range(round(days / dt)):
        ba = P["birth_a"] if t < reset_day else P["birth_a"] * reset_factor
        state = [max(x, 0.0)
                 for x in rk4_step(lambda s, u: deriv(s, u, birth_a=ba), state, t, dt)]
        t += dt
        ts.append(t)
        ys.append(state)
    return ts, ys

def sample(ts, ys, day):
    i = min(range(len(ts)), key=lambda k: abs(ts[k] - day))
    return ys[i]

# ── デモ / demo ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    ts, ys = simulate()
    labels = ["CAR-T", "memory", "naiveB", "autoPB", "protPC", "autoAb", "protAb"]
    print("compartments over time (illustrative units; X = exhaustion omitted):")
    print(f"  {'day':>4} | " + " ".join(f"{l:>7}" for l in labels))
    for d in (0, 7, 14, 30, 60, 120, 150, 250, 400):
        vals = sample(ts, ys, d)
        print(f"  {d:>4} | " + " ".join(f"{v:>7.1f}" for v in vals[:7]))

    naive = [y[2] for y in ys]
    cart = [y[0] for y in ys]
    nadir_i = min(range(len(naive)), key=lambda i: naive[i])
    peak_cart = max(cart)
    recovery = next((ts[i] for i in range(nadir_i, len(naive)) if naive[i] > N0 * 0.5), None)
    print(f"\npeak CAR-T expansion: x{peak_cart:.0f} at day {ts[cart.index(peak_cart)]:.0f}")
    print(f"B-cell nadir: {naive[nadir_i]:.0f} ({naive[nadir_i] / N0:.0%} of baseline) "
          f"at day {ts[nadir_i]:.0f}")
    print(f"B-cell reconstitution to 50%: day {recovery:.0f}"
          if recovery else "B cells stay depleted (persistent aplasia)")

    auto_drop = 1 - sample(ts, ys, 400)[5] / Aa0
    prot_keep = sample(ts, ys, 400)[6] / Ap0
    print(f"autoantibody (anti-dsDNA analogue): {auto_drop:.0%} lower at day 400")
    print(f"protective antibody (vaccine analogue): {prot_keep:.0%} of baseline retained")
    print("""
→ CAR-T は疲弊により一過性 (数ヶ月で消失)、B細胞は骨髄から再構築される
→ CD19+ 標的は枯渇するが CD19- の長寿命形質細胞は温存 → 自己抗体は落ち、
  ワクチン抗体は保たれる (臨床所見と一致)
→ リセット前 (~150日) に B が戻ると自己抗体が一時再上昇しうるが、再生した
  ナイーブレパートリーは自己反応性が低く、以後は病気が再燃しにくい
  — これが「免疫のリセット」の細胞的な実体""")
