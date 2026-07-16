"""
双安定知覚 / Bistable perception: binocular rivalry as attractor dynamics

同じ刺激が交互に見える両眼視野闘争 (やネッカーキューブ) を、相互抑制と
神経順応 (adaptation) を持つ2つの神経集団のダイナミクスとして再現するデモ。
入力が一定でも、意識に上る内容が自発的に交替する — 一定の刺激と揺らぐ意識の
乖離を示す。優位持続時間の分布 (右裾を引くガンマ様) も確認する。

⚠ 教育目的の簡略モデルです。
"""

import random

from info_theory import logistic

# ── 2集団の競合モデル / two mutually-inhibiting populations ──────────────
# dr_i/dt = (-r_i + σ(gain·(I − β·r_j − φ·a_i))) / τ_r
# da_i/dt = (-a_i + r_i) / τ_a        (神経順応: 発火が続くと自己抑制が溜まる)
I, BETA, PHI, GAIN = 1.0, 1.6, 1.35, 4.0
TAU_R, TAU_A, SIGMA, DT = 15.0, 3000.0, 0.5, 1.0   # 時定数 (ms), ノイズ
MIN_PERCEPT = 80   # 最小知覚持続時間 (ms): これ未満の反転は知覚されない (生理的な下限)

def simulate(ms=90000, seed=1):
    rng = random.Random(seed)
    r1, r2, a1, a2 = 0.9, 0.1, 0.0, 0.0          # 非対称な初期条件
    dominance = []
    for _ in range(int(ms / DT)):
        n1, n2 = rng.gauss(0, SIGMA), rng.gauss(0, SIGMA)
        dr1 = (-r1 + logistic(GAIN * (I - BETA * r2 - PHI * a1) + n1)) / TAU_R
        dr2 = (-r2 + logistic(GAIN * (I - BETA * r1 - PHI * a2) + n2)) / TAU_R
        da1 = (-a1 + r1) / TAU_A
        da2 = (-a2 + r2) / TAU_A
        r1 += DT * dr1; r2 += DT * dr2
        a1 += DT * da1; a2 += DT * da2
        dominance.append(1 if r1 > r2 else 2)
    return _despike(dominance)

def _despike(dom):
    """MIN_PERCEPT 未満の短い反転を直前の知覚に併合する (ノイズ由来の瞬間反転を除去)"""
    out = dom[:]
    i = 0
    while i < len(out):
        j = i
        while j < len(out) and out[j] == out[i]:
            j += 1
        if (j - i) * DT < MIN_PERCEPT and i > 0:
            for k in range(i, j):
                out[k] = out[i - 1]
        i = j
    return out

dom = simulate()

# ── 交替の時系列 / alternation time series (first 30 s) ─────────────────
print("perceptual dominance over the first 30 s (each column ≈ 0.4 s):")
window = dom[:30000]
step = max(1, len(window) // 75)
sampled = window[::step][:75]
print("  eye1 " + "".join("█" if d == 1 else " " for d in sampled))
print("  eye2 " + "".join("█" if d == 2 else " " for d in sampled))
print("       (only one percept is conscious at a time — they alternate)")

# ── 優位持続時間 / dominance durations ───────────────────────────────────
durations = []
cur, length = dom[0], 0
for d in dom:
    if d == cur:
        length += 1
    else:
        durations.append(length * DT / 1000.0)   # 秒
        cur, length = d, 1
durations.append(length * DT / 1000.0)

mean_dur = sum(durations) / len(durations)
sd = (sum((x - mean_dur) ** 2 for x in durations) / len(durations)) ** 0.5
print(f"\n{len(durations)} dominance periods in 90 s, "
      f"mean {mean_dur:.2f} s (CV {sd / mean_dur:.2f})")

# ── 持続時間の分布 / duration histogram ──────────────────────────────────
print("\ndominance-duration distribution (peaked around the adaptation timescale):")
bins = [(0, 0.5), (0.5, 1.0), (1.0, 1.5), (1.5, 2.5), (2.5, 4.0), (4.0, 99)]
for lo, hi in bins:
    c = sum(1 for d in durations if lo <= d < hi)
    label = f"{lo:.1f}-{hi:.1f}s" if hi < 99 else f"{lo:.1f}s+  "
    print(f"  {label:<9} {'#' * (c * 40 // len(durations))} {c}")
print("  (注: 実際の両眼視野闘争はより変動が大きく右に裾を引くガンマ分布。")
print("   この簡易モデルは交替の機構は捉えるが、変動の全体像はより精緻なモデルが要る)")

# ── 入力バランスと優位比 / input balance shifts dominance ────────────────
print("\neffect of unequal stimulus strength (eye-1 input) on eye-1 dominance:")
for i1 in (0.85, 0.95, 1.0, 1.05, 1.15):
    # 非対称入力でシミュレート (eye-1 の入力を i1、eye-2 を 1.0 に固定)
    rng = random.Random(2)
    r1, r2, a1, a2 = 0.5, 0.5, 0.0, 0.0
    frac1 = 0
    steps = int(20000 / DT)
    for _ in range(steps):
        n1, n2 = rng.gauss(0, SIGMA), rng.gauss(0, SIGMA)
        r1 += DT * (-r1 + logistic(GAIN * (i1 - BETA * r2 - PHI * a1) + n1)) / TAU_R
        r2 += DT * (-r2 + logistic(GAIN * (1.0 - BETA * r1 - PHI * a2) + n2)) / TAU_R
        a1 += DT * (-a1 + r1) / TAU_A
        a2 += DT * (-a2 + r2) / TAU_A
        frac1 += 1 if r1 > r2 else 0
    print(f"  eye-1 input {i1:.2f}: eye-1 dominant {frac1 / steps:.0%} of the time "
          f"{'#' * int(frac1 / steps * 30)}")
print("  (Levelt's law: stronger stimulus dominates a larger fraction of time)")

print("""
→ 入力は一定でも、相互抑制 + 順応 + ノイズにより意識内容が自発的に交替する
→ 優位持続時間には順応の時定数で決まる特徴的なスケールがある (実データはより変動大)
→ 刺激 (物理) と知覚 (意識) が1対1でない好例 — 意識の中身は脳の動態が決める
→ 意識の『内容 (何が見えるか)』を研究する窓: 神経相関 (NCC) 探索の古典的パラダイム""")
