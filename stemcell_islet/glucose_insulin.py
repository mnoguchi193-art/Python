"""
血糖-インスリン動態 / Glucose-insulin dynamics (a minimal model)

Bergman の最小モデルを土台に、β細胞量 (beta_mass) をパラメータとして
健常・1型糖尿病 (T1D)・膵島移植後の血糖応答を比較するデモ。
経口ブドウ糖負荷 (食事) に対する血糖曲線と血糖管理指標を計算する。
他モジュールの共有コア。

⚠ 教育目的の簡略モデル。パラメータは説明用の架空値で、臨床判断には使えません。
"""

# ── 汎用 RK4 積分器 / generic RK4 integrator ──────────────────────────────
def rk4_step(deriv, state, t, dt):
    k1 = deriv(state, t)
    k2 = deriv([s + 0.5 * dt * a for s, a in zip(state, k1)], t + 0.5 * dt)
    k3 = deriv([s + 0.5 * dt * a for s, a in zip(state, k2)], t + 0.5 * dt)
    k4 = deriv([s + dt * a for s, a in zip(state, k3)], t + dt)
    return [s + dt / 6 * (a + 2 * b + 2 * c + d)
            for s, a, b, c, d in zip(state, k1, k2, k3, k4)]

# ── パラメータ / parameters ──────────────────────────────────────────────
# 状態 = [G: 血糖 (mg/dL), X: インスリン作用, I: 血中インスリン (µU/mL)]
P = dict(
    SG=0.020,     # ブドウ糖自己排出 (glucose effectiveness) /min
    p2=0.025,     # インスリン作用の時定数 /min
    SI=6.0e-4,    # インスリン感受性 (per µU/mL) — T1D では不変、量が問題
    n=0.15,       # インスリンのクリアランス /min
    Gb=90.0,      # 基礎血糖 / basal glucose (mg/dL)
    Ib=10.0,      # 基礎インスリン / basal insulin (µU/mL)
    theta=90.0,   # 分泌が立ち上がる血糖閾値 / secretion threshold
    gamma=0.55,   # β細胞1単位あたりの分泌感度 / secretion sensitivity
)

def meal_Ra(t, carbs=60.0, t_meal=30.0, tau=45.0):
    """食事によるブドウ糖出現率 Ra(t) (mg/dL/min)。tau分でピークをとる吸収曲線。
    ガンマ様の形 A·(τ')·e^(-τ') で、ピーク時に約 carbs·0.09 mg/dL/min"""
    if t < t_meal:
        return 0.0
    u = (t - t_meal) / tau
    return carbs * 0.25 * u * pow(2.718281828, -u)

def make_deriv(beta_mass, p=P, exogenous_insulin=0.0, carbs=60.0):
    """β細胞量 beta_mass と外因性インスリン投与率から微分方程式を作る"""
    def deriv(state, t):
        G, X, I = state
        secretion = beta_mass * p["gamma"] * max(0.0, G - p["theta"])
        dG = -(p["SG"] + X) * G + p["SG"] * p["Gb"] + meal_Ra(t, carbs)
        dX = -p["p2"] * X + p["p2"] * p["SI"] * (I - p["Ib"])
        dI = secretion + exogenous_insulin - p["n"] * (I - p["Ib"])
        return [dG, dX, dI]
    return deriv

def simulate_meal(beta_mass, minutes=300, dt=0.5, exogenous_insulin=0.0,
                  carbs=60.0, G0=None, p=P):
    deriv = make_deriv(beta_mass, p, exogenous_insulin, carbs)
    G0 = p["Gb"] if G0 is None else G0
    state = [G0, 0.0, p["Ib"]]
    ts, ys = [0.0], [state]
    t = 0.0
    for _ in range(round(minutes / dt)):
        state = [max(x, 0.0) for x in rk4_step(deriv, state, t, dt)]
        t += dt
        ts.append(t)
        ys.append(state)
    return ts, ys

# ── 血糖管理指標 / glycemic metrics ──────────────────────────────────────
def metrics(ts, ys):
    G = [y[0] for y in ys]
    peak = max(G)
    in_range = sum(1 for g in G if 70 <= g <= 180) / len(G)   # TIR
    hyper = sum(1 for g in G if g > 180) / len(G)
    hypo = sum(1 for g in G if g < 70) / len(G)
    return dict(fasting=G[0], peak=peak, tir=in_range, hyper=hyper, hypo=hypo, end=G[-1])

# ── デモ / demo ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    scenarios = [
        ("healthy (beta=1.0)",        1.0, 0.0),
        ("T1D, no insulin (beta=0)",  0.0, 0.0),
        ("T1D + basal insulin only",  0.0, 1.0),
        ("islet graft (beta=0.4)",    0.4, 0.0),
    ]
    print("meal response (60 g carbs at t=30 min):")
    print(f"  {'scenario':<28} {'fasting':>8} {'peak':>6} {'TIR':>5} {'hyper':>6} {'hypo':>5}")
    curves = {}
    for name, beta, exo in scenarios:
        ts, ys = simulate_meal(beta, exogenous_insulin=exo)
        m = metrics(ts, ys)
        curves[name] = [y[0] for y in ys]
        print(f"  {name:<28} {m['fasting']:>7.0f}  {m['peak']:>5.0f} "
              f"{m['tir']:>5.0%} {m['hyper']:>5.0%} {m['hypo']:>5.0%}")

    print("\nglucose curves over 5 h (each column ≈ 6 min):")
    allG = [g for c in curves.values() for g in c]
    lo, hi = 60, max(allG)
    for name, c in curves.items():
        step = max(1, len(c) // 50)
        sampled = c[::step][:50]
        line = "".join("^" if g > 180 else ("_" if g < 70 else "-") for g in sampled)
        print(f"  {name:<28} {line}")
    print(f"  {'':<28} {'(- in range 70-180, ^ high, _ low)'}")
    print("\n→ β細胞ゼロ (T1D) では食後高血糖が遷延。基礎インスリンだけでは食後を抑えきれない")
    print("→ 移植したβ細胞は血糖に応答して分泌するため、生理的に近い管理が可能になる")
