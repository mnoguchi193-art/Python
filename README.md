# Python

Python の学習・参照用リポジトリです。基礎文法から、計算経済学・因果推論・計算社会科学・創薬・臨床予後・医療LLM までを、**外部ライブラリなし(標準ライブラリのみ)** で「動かして確かめられる」形にまとめています。

A Python learning and reference repository — from language basics to applied
computational science (economics, causal inference, computational social
science, drug discovery, clinical prognosis, and medical LLMs). Every module
is runnable with **the standard library only** and prints a worked example.

## 構成 / Structure

### Python の基礎 / Fundamentals

| Directory | Contents |
|---|---|
| [basics/](basics/) | data types, control flow, functions, comprehensions |
| [data_structures/](data_structures/) | stack, queue, linked list, binary search tree |
| [utilities/](utilities/) | file I/O, string helpers, datetime (JST) |
| [standard_library/](standard_library/) | collections, itertools, pathlib demos |

### 応用・研究分野 / Applied & research domains

| Directory | Theme | Contents |
|---|---|---|
| [mathematical_economics/](mathematical_economics/) | 数理経済学 | supply & demand, consumer & production theory, finance, game theory |
| [causal_inference/](causal_inference/) | 因果推論 | potential outcomes, RCT, difference-in-differences, IV, regression discontinuity |
| [computational_social_science/](computational_social_science/) | 計算社会科学・ビッグデータ | network analysis, text/TF-IDF, agent-based model, streaming sketches |
| [drug_discovery/](drug_discovery/) | 創薬・薬剤設計 | Lipinski rule of five, Tanimoto similarity, sequence alignment, pharmacology |
| [clinical_decision_support/](clinical_decision_support/) | 臨床意思決定支援・予後予測 | diagnostic test (Bayes), ROC/AUC, Kaplan-Meier, logistic risk score |
| [medical_llm/](medical_llm/) | 医療LLM・対話AI | BPE tokenizer, self-attention, decoding, RAG retrieval, dialogue safety |

## モジュール索引 / Module index

各応用分野の「何を計算するか → 主な関数/クラス → 前提とする仮定」です。

### mathematical_economics — 数理経済学
| File | 何を計算するか | 主な関数 / クラス | 前提・モデル |
|---|---|---|---|
| `supply_demand.py` | 市場均衡・余剰・弾力性 | `LinearMarket.equilibrium`, `consumer_surplus` | 線形の需要・供給 |
| `consumer_theory.py` | 効用最大化の最適消費 | `CobbDouglasConsumer.optimal_bundle` | コブ＝ダグラス効用・予算制約 |
| `production.py` | 限界生産物・規模の収穫 | `CobbDouglasProduction.returns_to_scale` | コブ＝ダグラス生産関数 |
| `finance.py` | 現在価値・NPV・IRR | `net_present_value`, `internal_rate_of_return` | 確定的キャッシュフロー |
| `game_theory.py` | ナッシュ均衡(純粋・混合) | `TwoByTwoGame.pure_nash`, `mixed_nash` | 2×2 標準形ゲーム |

### causal_inference — 因果推論
| File | 何を計算するか | 主な関数 / クラス | 前提・識別仮定 |
|---|---|---|---|
| `potential_outcomes.py` | ATE/ATT・選択バイアス分解 | `PotentialOutcomes.ate`, `selection_bias` | ルービン因果モデル |
| `randomized_experiment.py` | 平均処置効果と標準誤差 | `estimate_ate` | 無作為割付 |
| `difference_in_differences.py` | 差の差 | `did_from_means`, `did_from_data` | 平行トレンド |
| `instrumental_variables.py` | LATE / 2SLS | `wald_estimator`, `iv_2sls` | 操作変数の妥当性・除外制約 |
| `regression_discontinuity.py` | 閾値での処置効果 | `sharp_rdd` | 連続性・閾値での無作為性 |

### computational_social_science — 計算社会科学・ビッグデータ
| File | 何を計算するか | 主な関数 / クラス | 前提・手法 |
|---|---|---|---|
| `network.py` | 中心性・クラスタリング・連結成分 | `Graph.degree_centrality`, `connected_components` | 無向グラフ |
| `text_analysis.py` | TF-IDF による語の重み付け | `tf_idf`, `top_terms` | 単語バッグ表現 |
| `agent_based_model.py` | 分居の創発 | `Schelling.run`, `segregation` | セルオートマトン・局所規則 |
| `streaming.py` | 1パス・省メモリ集計 | `reservoir_sample`, `HyperLogLog`, `BloomFilter` | ストリーミング/スケッチ |

### drug_discovery — 創薬・薬剤設計
| File | 何を計算するか | 主な関数 / クラス | 前提・モデル |
|---|---|---|---|
| `lipinski.py` | 経口薬らしさの判定 | `molecular_weight`, `Molecule.is_drug_like` | ルール・オブ・ファイブ |
| `fingerprint_similarity.py` | 分子類似性・スクリーニング | `tanimoto`, `screen_library` | ビットフィンガープリント |
| `sequence_alignment.py` | 配列の大域アラインメント | `needleman_wunsch`, `identity` | 動的計画法・線形ギャップ |
| `pharmacology.py` | 用量反応・薬物動態 | `hill_response`, `OneCompartmentPK` | Hill式・1コンパートメント |

### clinical_decision_support — 臨床意思決定支援・予後予測
| File | 何を計算するか | 主な関数 / クラス | 前提・モデル |
|---|---|---|---|
| `diagnostic_test.py` | 感度/特異度・検査後確率 | `DiagnosticTest`, `post_test_probability` | ベイズの定理 |
| `roc_analysis.py` | 識別能(AUC)・最適閾値 | `auc`, `youden_threshold` | スコア付き二値分類 |
| `survival.py` | 生存曲線・生存期間中央値 | `KaplanMeier.survival_function` | 打ち切りあり・KM法 |
| `risk_score.py` | リスク予測・較正・有用性 | `LogisticRiskModel`, `brier_score`, `net_benefit` | ロジスティック回帰 |

### medical_llm — 医療LLM・対話AI
| File | 何を計算するか | 主な関数 / クラス | 前提・手法 |
|---|---|---|---|
| `tokenizer.py` | サブワード分割 | `BPETokenizer.train`, `encode` | バイトペア符号化 |
| `attention.py` | 自己注意 | `scaled_dot_product_attention` | Transformer の中核 |
| `sampling.py` | 次トークン選択 | `greedy`, `sample_top_k`, `sample_top_p` | softmax・温度・核サンプリング |
| `retrieval.py` | 知識への接地(RAG) | `TfidfRetriever.retrieve`, `build_prompt` | TF-IDF コサイン類似 |
| `triage.py` | 対話の安全層 | `assess` | ルールベースのガードレール |

## 分野を貫く数理 / Cross-cutting mathematics

同じ数学的道具が分野をまたいで再利用されています。

- **ベイズ更新 / Bayes** — `diagnostic_test`(検査後確率), `medical_llm/retrieval`(接地)
- **ロジスティック関数・softmax** — `clinical_decision_support/risk_score`, `medical_llm/sampling`, `attention`
- **TF-IDF・コサイン類似** — `computational_social_science/text_analysis`, `medical_llm/retrieval`
- **動的計画法 / DP** — `drug_discovery/sequence_alignment`(Needleman-Wunsch)
- **最小二乗・共分散** — `causal_inference/instrumental_variables`, `regression_discontinuity`, `mathematical_economics`
- **確率推定・サンプリング** — `computational_social_science/streaming`, `medical_llm/sampling`

## 実行方法 / How to Run

```bash
python basics/data_types.py
python mathematical_economics/supply_demand.py
python causal_inference/difference_in_differences.py
python computational_social_science/network.py
python drug_discovery/lipinski.py
python clinical_decision_support/diagnostic_test.py
python medical_llm/retrieval.py
```

各 `.py` は `python <path>` で単体実行でき、`if __name__ == "__main__"` のデモが動作します。
外部ライブラリは不要です(標準ライブラリのみ使用)。Python 3.10+ を想定しています。

## 注意 / Disclaimer

`drug_discovery`・`clinical_decision_support`・`medical_llm` は **教育・参照目的** の実装です。医療機器ではなく、診断・治療・処方の判断に用いるものではありません。実際の臨床判断は必ず資格を持つ医療専門家に相談してください。

These modules are for **education and reference only**. They are not medical
devices and must not be used for diagnosis, treatment, or prescribing.
