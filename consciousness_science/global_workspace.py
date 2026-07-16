"""
グローバルワークスペース理論 / Global Workspace Theory: ignition

意識的アクセスを「グローバルな点火 (ignition)」としてモデル化するデモ。
専門モジュールからの入力が閾値を超えると、再帰的増幅により全体が
非線形に『点火』し、情報が全脳に放送 (broadcast) される — 全か無かの
アクセス。弱い刺激は点火せず減衰する (サブリミナル=非意識的処理)。

⚠ 教育目的の簡略モデルです。
"""

from info_theory import logistic

# ── ワークスペースの再帰的ダイナミクス / recurrent workspace dynamics ────
# da/dt = -a + w·σ(gain·a + input − θ)
#   w が大きいと双安定 (低=非点火, 高=点火) になり、鋭い閾値が生じる。
W, GAIN, THETA, DT = 1.0, 8.0, 4.5, 0.1

def simulate_ignition(stimulus, steps=400, a0=0.0, stim_off=None):
    a, traj = a0, []
    for t in range(steps):
        inp = stimulus if (stim_off is None or t < stim_off) else 0.0
        a += DT * (-a + W * logistic(GAIN * a + inp - THETA))
        traj.append(a)
    return traj

# ── 刺激強度と点火 / stimulus strength vs ignition (all-or-none) ─────────
print("final workspace activation vs stimulus strength:")
print(f"  {'stimulus':>9} {'final act.':>11}  state")
threshold = None
for k in range(0, 17):
    stim = k * 0.25
    final = simulate_ignition(stim)[-1]
    ignited = final > 0.5
    if threshold is None and ignited:
        threshold = stim
    if k % 2 == 0:                       # 0.5 刻みで表示
        bar = "#" * int(final * 30)
        print(f"  {stim:>9.2f} {final:>11.3f}  {'IGNITED' if ignited else 'subthreshold':<12} {bar}")
print(f"→ 点火の閾値 ≈ 刺激強度 {threshold:.2f} 付近で、活動が全か無かで跳ね上がる")

# ── サブリミナル vs 意識的 / subliminal vs conscious time course ─────────
print("\ntime course (activation over time):")
sub = simulate_ignition(threshold - 0.6, stim_off=150)   # 閾値下: 減衰
sup = simulate_ignition(threshold + 0.6, stim_off=150)   # 閾値上: 点火・維持
for label, traj in [("subliminal (weak) ", sub), ("conscious (strong)", sup)]:
    step = max(1, len(traj) // 50)
    sampled = traj[::step][:50]
    line = "".join("█" if v > 0.5 else ("▄" if v > 0.15 else " ") for v in sampled)
    print(f"  {label} |{line}| peak {max(traj):.2f}")
print("  (stimulus removed at the midpoint; █ = ignited/broadcast)")

# ── 放送 = 複数モジュールが同時にアクセス / global broadcast ─────────────
DOWNSTREAM = ["言語report", "作業記憶", "行動制御", "エピソード記憶", "注意"]
print("\nonce ignited, content is broadcast to all modules (global availability):")
for stim, label in [(threshold - 0.6, "weak stimulus"), (threshold + 0.6, "strong stimulus")]:
    ignited = simulate_ignition(stim)[-1] > 0.5
    access = "  ".join(f"[{m}✓]" if ignited else f"[{m} ]" for m in DOWNSTREAM)
    print(f"  {label:<15}: {access}")

print("""
→ 点火は全か無か: 刺激がわずかに閾値を超えると活動が爆発的に立ち上がり自己維持する
→ 閾値下の刺激は局所処理されても点火せず減衰 — 情報処理はされるが意識に上らない
→ 点火した内容だけが言語報告・記憶・行動など多数のモジュールへ『放送』される
→ GWT は意識を『グローバルな利用可能性』とみなす — IIT (統合) とは別の視点""")
