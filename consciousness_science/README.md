# 意識科学 / The science of consciousness

意識をめぐる主要な計算理論を、標準ライブラリだけで動くモデルにした学習用デモ群です。
「意識の量」を測ろうとする統合情報理論、「意識的アクセス」を点火とみなす
グローバルワークスペース理論、意識の「内容」を探る双安定知覚、そして「自分の状態への
気づき」を扱う高次理論——異なる4つの視点を実装します。

> ⚠ **教育目的の大幅な簡略モデルです。** とくに Φ は本来の IIT 3.0/4.0 とは
> 異なる直観的近似です。パラメータは説明用の設定で、実データではありません。

## 構成 / Modules

| File | 内容 | 対応する理論 |
|---|---|---|
| `info_theory.py` | 共有コア。エントロピー・相互情報量・正規分布・ロジスティック | — |
| `integrated_information.py` | 統合情報量 Φ を小回路で計算。最小情報分割 (MIP) | 統合情報理論 (IIT) |
| `global_workspace.py` | 点火 (ignition) の全か無か・全脳放送 | グローバルワークスペース (GWT) |
| `bistable_perception.py` | 両眼視野闘争の自発的交替 (相互抑制 + 順応) | 意識の内容・NCC |
| `metacognition.py` | 一次感度 d' と二次のメタ認知感度の解離 | 高次理論 (HOT) |

## 実行 / Run

```bash
python consciousness_science/info_theory.py            # 情報理論の基礎
python consciousness_science/integrated_information.py  # Φ の計算 (IIT)
python consciousness_science/global_workspace.py        # 点火 (GWT)
python consciousness_science/bistable_perception.py      # 双安定知覚
python consciousness_science/metacognition.py           # メタ認知 (HOT)
```

外部ライブラリ不要 (標準ライブラリのみ)。各モジュールは `info_theory` を import する
ため、`consciousness_science/` をカレントに実行してください。

## 4つの視点 / Four windows on consciousness

1. **統合情報理論 (IIT)** — 意識の「量」は、システムが部分の寄せ集めを超えて統合する
   情報量 Φ に対応する。全結合の回路は Φ>0、フィードフォワードや分離系は Φ=0。
2. **グローバルワークスペース (GWT)** — 意識的アクセスは「点火」。刺激が閾値を超えると
   活動が全か無かで爆発し、内容が多数のモジュールへ放送される。閾値下は非意識的処理。
3. **意識の内容と NCC** — 一定の刺激でも知覚は自発的に交替する (両眼視野闘争)。
   意識の中身は物理刺激でなく脳の動態が決める。神経相関 (NCC) 探索の古典的窓。
4. **高次理論 (HOT)** — 意識は「自分の状態への気づき」。課題成績 (d') を保ったまま
   メタ認知だけが失われる解離 (盲視的) は、性能と意識が別物であることを示す。

**「意識とは何か」に唯一の答えはまだない。** これらは競合しつつ、それぞれが
意識の異なる側面 (量・アクセス・内容・気づき) を定量化しようとする試みです。
