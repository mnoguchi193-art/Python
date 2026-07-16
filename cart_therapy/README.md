# CAR-T 細胞療法と免疫のリセット / CAR-T therapy & immune reset

CAR-T (キメラ抗原受容体 T 細胞) 療法の力学を、標準ライブラリだけで解ける
小さな数理モデルとして実装した学習用デモ群です。近年、白血病・リンパ腫だけでなく
**自己免疫疾患 (ループス等) で「免疫系のリセット」** として使われ始めた機序を、
細胞・分子の動態から追えるようにしています。

> ⚠ **教育目的の簡略モデルです。** パラメータはすべて説明用の架空値で、
> 実際の細胞数・薬物動態・臨床判断を表すものではありません。
> 参考にした臨床像: Mackensen et al. *Nat Med* 2022 / Müller et al. *NEJM* 2024。

## 構成 / Modules

| File | 内容 |
|---|---|
| `cell_kinetics.py` | 共有コア。RK4 積分器と CAR-T ↔ 標的細胞の動態 (増殖→ピーク→収縮→メモリー残存) |
| `bcell_reset.py` | B細胞の枯渇と再構築。CD19- 長寿命形質細胞の温存、レパートリーの初期化 |
| `crs_dynamics.py` | サイトカイン放出症候群 (CRS)。腫瘍量依存の重症度、トシリズマブ介入 |
| `autoimmune_reset.py` | ループス (SLE) への応用。抗dsDNA・補体C3・SLEDAI、薬剤フリー寛解 |

## 実行 / Run

```bash
python cart_therapy/cell_kinetics.py      # CAR-T の基本動態
python cart_therapy/bcell_reset.py        # B細胞リセット
python cart_therapy/crs_dynamics.py       # CRS と介入
python cart_therapy/autoimmune_reset.py   # SLE の薬剤フリー寛解
```

外部ライブラリ不要 (標準ライブラリのみ)。`bcell_reset` と `crs_dynamics`,
`autoimmune_reset` は `cell_kinetics` / `bcell_reset` を import するため、
`cart_therapy/` をカレントに実行してください。

## モデルの要点 / Key ideas

- **一過性の CAR-T**: 増殖に伴う *疲弊 (exhaustion)* を状態変数で表現し、抗原が
  再生しても CAR-T が再拡大せず数ヶ月で消失する挙動を再現。自己免疫応用で
  B 細胞が回復する (=無形成が永続しない) 理由を機構的に示す。
- **選択的な枯渇**: CD19+ の B細胞・自己反応性形質芽細胞は枯渇するが、CD19- の
  長寿命形質細胞は温存 → 自己抗体は下がりワクチン抗体は保たれる。
- **リセットの実体**: 再生したナイーブ B レパートリーは自己反応性クローンが少なく、
  B 細胞が戻っても再燃しにくい。「抑え続ける」従来治療との機序的な違い。
- **効果と毒性の表裏**: 抗腫瘍/抗自己免疫の効果と CRS は同じ T 細胞活性化から
  生じ、完全には切り離せない。
