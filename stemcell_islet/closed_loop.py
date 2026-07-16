"""
1日の血糖コントロール / A day of glucose control across therapies

血糖-インスリンコアを使い、3食を含む24時間の血糖推移を
(1) 健常、(2) T1D + インスリンポンプ/注射、(3) T1D + 膵島移植 (血糖応答性)
で比較し、TIR (目標域内時間)・推定HbA1c・低血糖時間を計算するデモ。

⚠ 教育目的の簡略モデル。パラメータは説明用の架空値で、臨床判断には使えません。
"""

from glucose_insulin import P, rk4_step

# ── 1日の食事 / meals over a day (minutes from midnight) ─────────────────
MEALS = [(7 * 60, 55), (12 * 60, 70), (19 * 60, 65)]  # (時刻, 炭水化物g)

def meals_Ra(t, tau=45.0):
    total = 0.0
    for t_meal, carbs in MEALS:
        if t >= t_meal:
            u = (t - t_meal) / tau
            total += carbs * 0.25 * u * pow(2.718281828, -u)
    return total

# ── インスリン投与 / insulin delivery ────────────────────────────────────
CR_STRENGTH = 0.04   # 低血糖時の肝ブドウ糖放出 (拮抗調節) / counter-regulation
CR_THRESHOLD = 80.0  # これを下回ると肝が糖を放出しはじめる

def counter_regulation(G):
    """血糖が下がると肝がブドウ糖を放出して低血糖を緩和する (生理的な下限)"""
    return CR_STRENGTH * max(0.0, CR_THRESHOLD - G)

def pump_insulin(t, G):
    """ポンプ/注射: 基礎 + 食事ボーラス。実際にはやや遅れ・過少投与がある"""
    basal = 0.5
    bolus = 0.0
    for t_meal, carbs in MEALS:
        # ボーラスは食事の少し後に立ち上がり、必要量を完全にはカバーしない (現実的な不完全さ)
        delay = 12.0
        if t >= t_meal + delay:
            u = (t - t_meal - delay) / 55.0
            bolus += carbs * 0.40 * u * pow(2.718281828, -u)
    return basal + bolus

def simulate_day(mode, beta_mass=0.0, minutes=1440, dt=0.5, p=P):
    """mode: 'healthy' | 'pump' | 'graft'"""
    state = [p["Gb"], 0.0, p["Ib"]]
    ts, ys = [0.0], [state]
    t = 0.0
    for _ in range(round(minutes / dt)):
        G, X, I = state
        if mode == "healthy":
            secretion, exo = 1.0 * p["gamma"] * max(0.0, G - p["theta"]), 0.0
        elif mode == "graft":
            secretion, exo = beta_mass * p["gamma"] * max(0.0, G - p["theta"]), 0.0
        else:  # pump
            secretion, exo = 0.0, pump_insulin(t, G)
        def deriv(s, tt):
            g, x, i = s
            dG = (-(p["SG"] + x) * g + p["SG"] * p["Gb"]
                  + meals_Ra(tt) + counter_regulation(g))
            dX = -p["p2"] * x + p["p2"] * p["SI"] * (i - p["Ib"])
            dI = secretion + exo - p["n"] * (i - p["Ib"])
            return [dG, dX, dI]
        state = [max(v, 0.0) for v in rk4_step(deriv, state, t, dt)]
        t += dt
        ts.append(t)
        ys.append(state)
    return ts, ys

def day_metrics(ts, ys):
    G = [y[0] for y in ys]
    mean = sum(G) / len(G)
    hba1c = (mean + 46.7) / 28.7          # 推定HbA1c (%) / estimated A1c
    tir = sum(1 for g in G if 70 <= g <= 180) / len(G)
    hypo = sum(1 for g in G if g < 70) / len(G)
    hyper = sum(1 for g in G if g > 180) / len(G)
    return dict(mean=mean, hba1c=hba1c, tir=tir, hypo=hypo, hyper=hyper,
                peak=max(G), nadir=min(G))

# ── 比較 / comparison ────────────────────────────────────────────────────
scenarios = [
    ("healthy",                     "healthy", 0.0),
    ("T1D + pump/injection",        "pump",    0.0),
    ("T1D + islet graft (β=0.45)",  "graft",   0.45),
]
print("24-hour glucose control (3 meals):")
print(f"  {'therapy':<28} {'mean':>5} {'A1c':>5} {'TIR':>5} {'hyper':>6} {'hypo':>5} {'peak':>5}")
curves = {}
for label, mode, beta in scenarios:
    ts, ys = simulate_day(mode, beta_mass=beta)
    m = day_metrics(ts, ys)
    curves[label] = [y[0] for y in ys]
    print(f"  {label:<28} {m['mean']:>5.0f} {m['hba1c']:>4.1f}% {m['tir']:>5.0%} "
          f"{m['hyper']:>5.0%} {m['hypo']:>4.0%} {m['peak']:>5.0f}")

# ── 24時間の血糖曲線 / 24-hour glucose tracing ───────────────────────────
print("\nglucose over 24 h (each column = ~30 min; ^ >180, _ <70, - in range):")
for label, c in curves.items():
    step = max(1, len(c) // 48)
    sampled = c[::step][:48]
    line = "".join("^" if g > 180 else ("_" if g < 70 else "-") for g in sampled)
    print(f"  {label:<28} {line}")
print(f"  {'':<28} {'0h    6h    12h   18h   24h':<48}")
print("        (meals at 7:00, 12:00, 19:00)")

print("""
→ ポンプ/注射は食事ボーラスの遅れ・過少で食後高血糖を生じる。これを抑えようと
  増量すると今度は食間の低血糖を招く — 開ループ投与のトレードオフ
  (患者が炭水化物計算と投与量調整を担い続ける負担も大きい)
→ 移植したβ細胞は血糖をリアルタイムに感知して分泌を自動調整する「生物学的閉ループ」
  → 高血糖と低血糖のトレードオフから解放され、TIR が高く低血糖リスクも小さい
→ 幹細胞由来膵島は、この生理的な血糖応答を無制限の細胞供給で実現しようとする試み
  (課題は分化収率・移植片生存・免疫回避 — 他モジュール参照)""")
