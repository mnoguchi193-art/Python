# AGI Algorithms (AGI の基礎アルゴリズム)

AGI (汎用人工知能) そのものは未だ実現されていませんが、その研究の土台となる
代表的なアルゴリズムを、標準ライブラリのみで学習用に実装しています。

Educational implementations of the foundational algorithms behind AGI research,
using only the Python standard library.

| File | Algorithm | AGI との関わり |
|---|---|---|
| [q_learning.py](q_learning.py) | Q学習 (強化学習) | 試行錯誤による自律的な学習 |
| [neural_network.py](neural_network.py) | ニューラルネットワーク + 誤差逆伝播 | 深層学習・LLM の中核となる仕組み |
| [search_planning.py](search_planning.py) | A* 探索 / STRIPS 風プランナー | 目標達成のための計画立案 |
| [inference_engine.py](inference_engine.py) | 前向き・後ろ向き推論 | 知識からの論理的推論 (記号的 AI) |
| [genetic_algorithm.py](genetic_algorithm.py) | 遺伝的アルゴリズム | 進化による解の自動発見 |
| [cognitive_agent.py](cognitive_agent.py) | 認知アーキテクチャ | 知覚・記憶・推論・計画・学習の統合 |

## 実行方法 / How to Run

```bash
python agi/q_learning.py
python agi/neural_network.py
python agi/search_planning.py
python agi/inference_engine.py
python agi/genetic_algorithm.py
python agi/cognitive_agent.py
```

各ファイルは独立して実行でき、外部ライブラリは不要です。

## 学習の流れ (おすすめの読む順)

1. **search_planning.py** — 探索は最も古典的な AI 手法
2. **inference_engine.py** — 記号的 AI (ルールベース) の考え方
3. **genetic_algorithm.py** — 最適化・自動発見のアプローチ
4. **neural_network.py** — 現代の深層学習の原点
5. **q_learning.py** — 環境との相互作用から学ぶ強化学習
6. **cognitive_agent.py** — 上記の機能を1つのループに統合
