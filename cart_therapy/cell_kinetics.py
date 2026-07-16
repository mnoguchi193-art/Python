"""
CAR-T 細胞の動態 / CAR-T cell kinetics: expansion, contraction, persistence

抗原 (標的 CD19+ 細胞) に駆動された CAR-T 細胞の増殖 → ピーク → 収縮 →
メモリーによる長期残存を、常微分方程式 (ODE) を RK4 で解いて再現するデモ。
CAR-T 療法の PK/PD の骨格であり、他のモジュールの共有コア。

⚠ 教育目的の簡略モデルです。パラメータは説明用の架空値で、
   臨床的判断には使えません / illustrative model — not for clinical use.
"""

# ── 汎用 RK4 積分器 / generic RK4 integrator ──────────────────────────────
def rk4_step(deriv, state, t, dt):
    k1 = deriv(state, t)
    k2 = deriv([s + 0.5 * dt * a for s, a in zip(state, k1)], t + 0.5 * dt)
    k3 = deriv([s + 0.5 * dt * a for s, a in zip(state, k2)], t + 0.5 * dt)
    k4 = deriv([s + dt * a for s, a in zip(state, k3)], t + dt)
    return [s + dt / 6 * (a + 2 * b + 2 * c + d)
            for s, a, b, c, d in zip(state, k1, k2, k3, k4)]

def integrate(deriv, state0, t0, t1, dt):
    """[t0, t1] を dt 刻みで積分し、(times, states) を返す"""
    ts, ys = [t0], [list(state0)]
    state, t = list(state0), t0
    for _ in range(round((t1 - t0) / dt)):
        state = [max(x, 0.0) for x in rk4_step(deriv, state, t, dt)]  # 個数は非負
        t += dt
        ts.append(t)
        ys.append(state)
    return ts, ys

# ── CAR-T ↔ 標的細胞モデル / CAR-T vs target-cell dynamics ────────────────
# 状態 = [C: エフェクター CAR-T, M: メモリー CAR-T, B: 標的 CD19+ 細胞]
#   単位はすべて相対濃度 (cells/µL 相当)
PARAMS = dict(
    rho=1.20,    # 抗原駆動の増殖率 / antigen-driven proliferation
    delta_c=0.30,  # エフェクターの死滅率 / effector death
    mu=0.15,     # エフェクター→メモリーへの分化 / differentiation to memory
    alpha=0.60,  # 抗原再曝露でのメモリー再活性化 / memory re-activation
    delta_m=0.02,  # メモリーの緩やかな減衰 / slow memory decay
    Kb=50.0,     # 抗原の半飽和定数 / half-saturation of antigen signal
    r=0.30,      # 標的細胞の増殖率 (腫瘍なら増殖) / target growth
    Bmax=1000.0,  # 標的細胞のキャパシティ / carrying capacity
    kappa=0.025,  # CAR-T による殺傷効率 / killing efficiency
)

def cart_deriv(state, t, p=PARAMS):
    C, M, B = state
    signal = B / (B + p["Kb"])          # 抗原シグナルの強さ (0..1)
    dC = (p["rho"] * signal * C          # 抗原があれば増殖
          + p["alpha"] * signal * M      # メモリーが再活性化して合流
          - p["mu"] * (1 - signal) * C   # 抗原が減るとメモリーへ分化
          - p["delta_c"] * C)            # 自然死
    dM = (p["mu"] * (1 - signal) * C     # エフェクターから供給
          - p["alpha"] * signal * M      # 再活性化で流出
          - p["delta_m"] * M)            # 緩やかに減衰
    dB = p["r"] * B * (1 - B / p["Bmax"]) - p["kappa"] * C * B  # 増殖 − 殺傷
    return [dC, dM, dB]

def simulate_infusion(dose=1.0, tumor_burden=800.0, days=120, dt=0.05, p=PARAMS,
                      eradication_floor=1.0):
    """CAR-T を dose だけ投与し、経過を積分する。

    標的が eradication_floor を下回ったら 0 に固定する — 決定論 ODE が
    無限小の残存で平衡するのを避け、最後の細胞の確率的消失を近似する。
    """
    deriv = lambda s, t: cart_deriv(s, t, p)
    ts, ys = [0.0], [[dose, 0.0, tumor_burden]]
    state, t = [dose, 0.0, tumor_burden], 0.0
    for _ in range(round(days / dt)):
        state = [max(x, 0.0) for x in rk4_step(deriv, state, t, dt)]
        if 0 < state[2] < eradication_floor:
            state[2] = 0.0  # 根絶 / eradicated
        t += dt
        ts.append(t)
        ys.append(state)
    return ts, ys

# ── デモ / demo ──────────────────────────────────────────────────────────
def _sparkline(values, width=50, height=6):
    """時系列を ASCII で概観 / crude ASCII plot"""
    lo, hi = min(values), max(values)
    span = hi - lo or 1.0
    step = max(1, len(values) // width)
    sampled = values[::step][:width]
    rows = []
    for level in range(height, 0, -1):
        thresh = lo + span * (level - 0.5) / height
        rows.append("".join("#" if v >= thresh else " " for v in sampled))
    return rows, lo, hi

if __name__ == "__main__":
    ts, ys = simulate_infusion()
    C = [y[0] for y in ys]
    M = [y[1] for y in ys]
    B = [y[2] for y in ys]

    peak_c = max(C)
    peak_day = ts[C.index(peak_c)]
    # 標的が初期の1%まで減った日 = 寛解達成の目安
    clear_day = next((ts[i] for i, b in enumerate(B) if b < B[0] * 0.01), None)
    day90 = min(range(len(ts)), key=lambda i: abs(ts[i] - 90))

    print("CAR-T infusion simulation (illustrative):")
    print(f"  peak CAR-T expansion : {peak_c:6.1f} at day {peak_day:.0f} "
          f"(x{peak_c:.0f} over infused dose)")
    print(f"  tumor cleared (<1%)  : day {clear_day:.0f}"
          if clear_day else "  tumor NOT cleared")
    print(f"  CAR-T at day 90      : effector {C[day90]:.2f}, memory {M[day90]:.2f} "
          f"(persistence)")

    print("\nCAR-T effector count over 120 days:")
    rows, lo, hi = _sparkline(C)
    for row in rows:
        print(f"  {row}")
    print(f"  day 0{'.' * 42}day 120   (peak {hi:.0f})")

    print("\ntumor burden over 120 days:")
    rows, lo, hi = _sparkline(B)
    for row in rows:
        print(f"  {row}")
    print(f"  day 0{'.' * 42}day 120   (start {B[0]:.0f} → end {B[-1]:.1f})")

    print("\n→ 抗原に駆動され CAR-T は数十倍に増殖し、標的を排除後は収縮、")
    print("  一部がメモリーとして残る。この残存が「免疫のリセット」を可能にする")
