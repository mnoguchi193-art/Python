"""
準種と誤り破局 / Quasispecies and the error catastrophe (Eigen)

複製の忠実度と情報の維持の関係をモデル化するデモ。Eigen の準種理論では、
1塩基あたりの複製忠実度 q・ゲノム長 L・マスター配列の優位性 σ が
『情報を維持できるか』を決める。誤り率がある閾値を超えると、選択されていた
マスター配列が突然失われる (誤り破局) — これが原始的な複製系の情報量に上限を課す。

⚠ 教育目的の簡略モデルです。
"""

import math

# ── マスター配列の平衡頻度 / equilibrium master fraction ─────────────────
# Q = q^L : ゲノム全体を無誤りで複製する確率。
# マスターは適応度 σ、変異雲は適応度 1。逆変異は無視 (近似)。
# 平衡: x_m* = (σQ − 1)/(σ − 1)  (σQ>1 のときのみ正、さもなくば 0 = 誤り破局)。
def master_fraction(q, L, sigma):
    Q = q ** L
    if sigma * Q <= 1:
        return 0.0
    return (sigma * Q - 1) / (sigma - 1)

def critical_length(q, sigma):
    """情報を維持できる最大ゲノム長 L_max = ln σ / (1 − q) の近似"""
    return math.log(sigma) / (1 - q)

# ── ゲノム長 vs 情報維持 / genome length and the threshold ───────────────
SIGMA = 10.0     # マスター配列の適応度優位性
Q_FID = 0.99     # 1塩基あたりの複製忠実度 (誤り率 1%)

print(f"master-sequence survival vs genome length (fidelity q={Q_FID}, σ={SIGMA}):")
print(f"  {'genome length L':>16} {'error-free Q=q^L':>16} {'master fraction':>16}")
Lc = critical_length(Q_FID, SIGMA)
for L in (50, 100, 200, Lc, 300, 400):
    xm = master_fraction(Q_FID, int(round(L)), SIGMA)
    marker = "  ← L_max (threshold)" if abs(L - Lc) < 1 else ""
    bar = "#" * int(xm * 30)
    print(f"  {L:>16.0f} {Q_FID ** L:>16.3f} {xm:>15.1%}  {bar}{marker}")
print(f"→ 臨界長 L_max ≈ {Lc:.0f} 塩基。これを超えるとマスター配列が消える (誤り破局)")

# ── 誤り率を上げていくと / raising the mutation rate ─────────────────────
L_FIXED = 100
print(f"\nfixed genome length L={L_FIXED}: master fraction vs per-base error rate:")
print(f"  {'error rate (1−q)':>16} {'master fraction':>16}")
for err in (0.005, 0.01, 0.02, 0.023, 0.03, 0.05):
    q = 1 - err
    xm = master_fraction(q, L_FIXED, SIGMA)
    bar = "#" * int(xm * 30)
    state = "" if xm > 0 else "  (catastrophe)"
    print(f"  {err:>16.1%} {xm:>15.1%}  {bar}{state}")
threshold_err = 1 - (1 / SIGMA) ** (1 / L_FIXED)
print(f"→ 誤り率の閾値 ≈ {threshold_err:.1%}。これを超えると情報が保てない")

# ── 変異-選択のダイナミクス / mutation-selection dynamics ────────────────
def simulate(q, L, sigma, gens=60, x0=0.9):
    """世代ごとにマスター頻度を更新して平衡に至る過程"""
    Q = q ** L
    x = x0
    traj = [x]
    for _ in range(gens):
        master = sigma * Q * x
        mutant = sigma * (1 - Q) * x + 1 * (1 - x)
        x = master / (master + mutant)
        traj.append(x)
    return traj

print("\nmaster-fraction dynamics (L=100), below vs above the error threshold:")
for err, label in [(0.01, "below (q=0.99)"), (0.03, "above (q=0.97)")]:
    traj = simulate(1 - err, L_FIXED, SIGMA)
    spark = "".join("█" if v > 0.5 else ("▄" if v > 0.1 else " ")
                    for v in traj[::max(1, len(traj) // 40)])
    print(f"  {label:<16} |{spark}| final {traj[-1]:.1%}")

print("""
→ 情報を持つ複製子には『複製の正確さ × ゲノム長』の上限がある (誤り破局)
→ 忠実度が低い原始的な複製系は、短い情報しか保てない — 複雑化の壁
→ 逆に、より長いゲノムには高い忠実度 (酵素) が要り、その酵素はゲノムが要る…
  = 『Eigen のパラドックス』。区画化や自己触媒集合がこの袋小路を破る鍵とされる""")
