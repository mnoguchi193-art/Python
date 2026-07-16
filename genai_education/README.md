# 生成AIと教育格差 / Generative AI and educational inequality

生成AI (genAI) が教育格差を**広げるのか縮めるのか**を、生徒集団の
エージェントベースモデルで分析する学習用デモ群です。社会経済的地位 (SES) と
相関する属性を持つ生徒を生成し、アクセス格差・学習成果・累積動学・政策介入を
標準ライブラリだけでシミュレートします。

> ⚠ **教育目的の簡略モデルです。** パラメータはすべて説明用の架空値で、
> 実証研究の推定値ではありません。

## 構成 / Modules

| File | 内容 |
|---|---|
| `access_model.py` | 共有コア。SESと相関する生徒集団の生成、アクセス確率・利用の質、格差指標 |
| `learning_gains.py` | genAIの学習効果。補償的潜在力 vs 実際のゲイン、格差は広がるか縮むか |
| `divide_dynamics.py` | 累積的格差の動学。マタイ効果で格差が複利的に拡大/縮小する軌跡 |
| `policy_simulation.py` | 政策レバー (アクセス補助・AIリテラシー・指導支援・足場かけ) の比較 |

## 実行 / Run

```bash
python genai_education/access_model.py        # アクセス格差 (二重のデバイド)
python genai_education/learning_gains.py       # 格差を広げるか縮めるか
python genai_education/divide_dynamics.py       # 累積動学 (マタイ効果)
python genai_education/policy_simulation.py     # 政策介入の比較
```

外部ライブラリ不要 (標準ライブラリのみ)。各モジュールは `access_model` を
import するため、`genai_education/` をカレントに実行してください。

## 中心的な論点 / The core argument

1. **二重のデジタル・デバイド** (`access_model.py`) — アクセスの格差 (第一) に加え、
   同じツールを『使いこなす質』の格差 (第二) が重なり、どちらも高SES層に偏る。
2. **潜在力と現実の逆転** (`learning_gains.py`) — genAIは本来「遅れた生徒ほど伸びる」
   補償的な潜在力を持つ (Bloomの2シグマ)。だが放任するとアクセス×質の偏りで
   潜在力が逆転し、**格差はむしろ拡大する**。
3. **累積するからこそ早期介入** (`divide_dynamics.py`) — 学力→利用の質→ゲインの
   正のフィードバック (マタイ効果) が、わずかな差を数年で大きな格差に育てる。
4. **公平と効率は両立しうる** (`policy_simulation.py`) — アクセス補助だけでは不十分。
   低SES層への指導支援や足場かけを組み合わせると、格差を縮めつつ全体の伸びも最大化。

**技術そのものは中立で、格差の向きを決めるのは『アクセスと使い方の分配』である**
— というのが一連のモデルが示すメッセージです。
