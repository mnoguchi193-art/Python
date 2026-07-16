"""
サイトカイン放出症候群 / Cytokine release syndrome (CRS)

CAR-T の増殖と標的細胞の量に駆動される IL-6 の急上昇と、その重症度グレード、
そして抗 IL-6 受容体抗体 (トシリズマブ) 介入の効果をシミュレートするデモ。
腫瘍量 (抗原量) が CRS の最大のリスク因子であることを示す。

⚠ 教育目的の簡略モデル。パラメータは説明用の架空値で、臨床判断には使えません。
"""

from cell_kinetics import PARAMS, simulate_infusion

# ── IL-6 の動態 / IL-6 kinetics ──────────────────────────────────────────
# CAR-T が標的に会合して活性化すると、骨髄系細胞 (マクロファージ) を介して
# IL-6 が放出される。放出量は「CAR-T 量 × 抗原シグナル」に比例させる。
K_REL = 0.20     # CAR-T 活性化による放出 / activation-driven release
K_LYS = 0.090    # 標的細胞の崩壊 (DAMPs) による放出 / tumor-lysis release
IL6_CLEAR = 1.5  # IL-6 のクリアランス率/日 / clearance
TOCI_BLOCK = 0.2  # トシリズマブ投与後に残る IL-6 受容体シグナル / residual signaling
KB = PARAMS["Kb"]
KAPPA = PARAMS["kappa"]

def il6_trajectory(tumor_burden, toci_threshold=None, days=30, dt=0.02):
    """CAR-T/標的の軌跡から IL-6 と CRS 重症度を計算する。

    toci_threshold を与えると、CRS 重症度がその値を超えた時点で
    トシリズマブを投与し、以後 IL-6 受容体シグナル (=臨床的重症度) を抑える。
    """
    ts, ys = simulate_infusion(tumor_burden=tumor_burden, days=days, dt=dt)
    il6, severity = 0.0, []
    toci_given_day = None
    for k, (t, (C, M, B)) in enumerate(zip(ts, ys)):
        signal = B / (B + KB)
        release = K_REL * C * signal + K_LYS * KAPPA * C * B  # 活性化 + 腫瘍崩壊
        il6 += dt * (release - IL6_CLEAR * il6)
        # 臨床的重症度は IL-6 受容体シグナルで決まる。トシリズマブは受容体を遮断し
        # 血中 IL-6 自体は下げないが、下流のシグナル (=症状) を抑える。
        blocked = toci_given_day is not None and t >= toci_given_day
        effective = il6 * (TOCI_BLOCK if blocked else 1.0)
        if toci_threshold is not None and toci_given_day is None \
                and grade(effective)[0] >= toci_threshold:
            toci_given_day = t
        severity.append((t, il6, effective))
    return severity, toci_given_day

def grade(effective_il6):
    """実効 IL-6 シグナルを CRS グレード (ASTCT 風の連続近似) に対応づける"""
    x = effective_il6
    if x < 5:  return 0, "none"
    if x < 11: return 1, "fever only"
    if x < 16: return 2, "hypotension / O2"
    if x < 22: return 3, "vasopressors"
    return 4, "ICU / ventilation"

# ── 腫瘍量による CRS リスク / burden is the key risk factor ──────────────
print("CRS severity vs tumor burden (antigen load):")
print(f"  {'burden':>7} {'peak IL-6':>10} {'peak grade':>11}  {'clinical':<18}")
for burden in (100, 300, 600, 900):
    sev, _ = il6_trajectory(burden)
    peak_il6 = max(s[1] for s in sev)
    g, desc = grade(peak_il6)
    print(f"  {burden:>7} {peak_il6:>10.1f} {'grade ' + str(g):>11}  {desc:<18}  {'#' * (g * 6)}")
print("→ 高腫瘍量ほど CRS は重症化 — 事前の腫瘍減量 (debulking) が予防になる理由")

# ── トシリズマブ介入 / tocilizumab intervention ─────────────────────────
print("\nhigh-burden case (900) with vs without tocilizumab at grade 2:")
for label, thr in [("no intervention", None), ("toci at grade 2", 2)]:
    sev, toci_day = il6_trajectory(900, toci_threshold=thr)
    peak_eff = max(s[2] for s in sev)
    g, desc = grade(peak_eff)
    when = f", given day {toci_day:.1f}" if toci_day else ""
    print(f"  {label:<16}: peak grade {g} ({desc}){when}")

# ── IL-6 の時間経過 / IL-6 time course ───────────────────────────────────
sev, _ = il6_trajectory(900)
print("\nIL-6 over first 30 days (high burden):")
il6_series = [s[1] for s in sev]
hi = max(il6_series)
step = max(1, len(il6_series) // 50)
sampled = il6_series[::step][:50]
for level in range(5, 0, -1):
    thresh = hi * (level - 0.5) / 5
    print("  " + "".join("#" if v >= thresh else " " for v in sampled))
print(f"  day 0{'.' * 42}day 30   (peak IL-6 {hi:.0f})")
print("\n→ CRS は CAR-T 増殖のピーク (数日〜2週) に一致して立ち上がる")
print("→ 効果 (抗腫瘍/抗自己免疫) と CRS は同じ活性化の裏表 — 完全には切り離せない")
