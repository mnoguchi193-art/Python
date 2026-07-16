"""
自己免疫疾患のリセット / Resetting autoimmunity — a lupus (SLE) case

B細胞リセットの動態を全身性エリテマトーデス (SLE) の臨床指標に対応づけ、
抗dsDNA抗体・補体C3・疾患活動性 (SLEDAI) の推移と、免疫抑制薬なしでの
寛解 (drug-free remission) を「リセットあり/なし」で比較するデモ。

⚠ 教育目的の簡略モデル。パラメータは説明用の架空値で、臨床判断には使えません。
   参考にした臨床像: Mackensen et al. Nat Med 2022 / Müller et al. NEJM 2024
   (SLE 患者で単回 CD19 CAR-T により薬剤フリー寛解が報告された)
"""

from bcell_reset import Aa0, simulate, sample

# ── 免疫学的状態 → 臨床指標への対応 / mapping to clinical scores ──────────
def anti_dsdna(autoab):
    """自己抗体量 → 抗dsDNA抗体価 (IU/mL 相当)。>30 で陽性"""
    return 120.0 * autoab / Aa0            # 病前を 120 IU/mL とする

def complement_c3(autoab):
    """免疫複合体が補体を消費 → C3 は自己抗体と逆相関 (低值が活動性)"""
    normal, consumed = 120.0, 70.0        # mg/dL: 正常 120、活動期に消費で低下
    return normal - consumed * (autoab / Aa0)

def sledai(autoab, c3):
    """疾患活動性スコア (SLEDAI 風): 自己抗体高値 + 補体低下で上昇"""
    ab_term = 8.0 * (autoab / Aa0)                    # 抗体寄与
    c3_term = 6.0 * max(0.0, (100 - c3) / 100)        # 補体低下寄与
    organ = 4.0 * (autoab / Aa0) ** 1.5               # 臓器障害 (腎炎など)
    return ab_term + c3_term + organ

def activity_label(score):
    if score < 3:  return "remission"
    if score < 6:  return "mild"
    if score < 12: return "moderate"
    return "severe flare"

# ── リセットあり vs なし / with vs without repertoire reset ──────────────
scenarios = {
    "reset (tolerance re-established)": 0.25,  # 再生レパートリーの自己反応性 1/4
    "no reset (autoreactivity returns)": 1.0,  # 元のまま → B 回復で再燃
}

print("SLE disease course after CD19 CAR-T (illustrative):")
print(f"  {'':>5}| {'--- WITH reset ---':^22} | {'--- NO reset ---':^22}")
print(f"  {'day':>4}| {'dsDNA':>6} {'C3':>5} {'SLEDAI':>7} | {'dsDNA':>6} {'C3':>5} {'SLEDAI':>7}")

runs = {name: simulate(reset_factor=f) for name, f in scenarios.items()}
for d in (0, 30, 90, 180, 270, 400):
    cells = []
    for name in scenarios:
        ts, ys = runs[name]
        aa = sample(ts, ys, d)[5]
        c3 = complement_c3(aa)
        cells.append(f"{anti_dsdna(aa):>6.0f} {c3:>5.0f} {sledai(aa, c3):>7.1f}")
    print(f"  {d:>4}| " + " | ".join(cells))

# ── 転帰 / outcomes ──────────────────────────────────────────────────────
print("\noutcome at day 400 (off all immunosuppressants):")
for name in scenarios:
    ts, ys = runs[name]
    aa = sample(ts, ys, 400)[5]
    c3 = complement_c3(aa)
    s = sledai(aa, c3)
    print(f"  {name:<36}: SLEDAI {s:4.1f} → {activity_label(s)}")

# ── 疾患活動性の推移 / SLEDAI trajectory (reset case) ────────────────────
ts, ys = runs["reset (tolerance re-established)"]
scores = [sledai(y[5], complement_c3(y[5])) for y in ys]
hi = max(scores)
step = max(1, len(scores) // 50)
sampled = scores[::step][:50]
print("\nSLEDAI over 400 days (reset case):")
for level in range(6, 0, -1):
    thresh = hi * (level - 0.5) / 6
    print("  " + "".join("#" if v >= thresh else " " for v in sampled))
print(f"  day 0{'.' * 42}day 400   (baseline SLEDAI {scores[0]:.0f} → remission)")

print("""
→ 抗dsDNA抗体は数週で低下し、消費されていた補体C3が正常化 → SLEDAI が寛解域へ
→ 「リセットあり」では B 細胞が戻っても再燃しない (薬剤フリー寛解) が、
  「リセットなし」では自己反応性クローンが再生して疾患が再燃する
→ 従来の免疫抑制は「免疫を抑え続ける」治療。CAR-T リセットは自己反応性の
  記憶・産生細胞を一掃し、寛容を再構築しうる点で機序的に異なる
→ ただし CRS 等のリスクを伴い (crs_dynamics.py 参照)、適応は慎重に判断される""")
