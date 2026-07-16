# 幹細胞由来膵島細胞による1型糖尿病治療 / Stem-cell-derived islets for T1D

多能性幹細胞から分化させた膵島β細胞を移植して1型糖尿病 (T1D) を治療する
アプローチ (Vertex の VX-880/zimislecel やカプセル化デバイス等) の要素を、
標準ライブラリだけで解ける小さな数理モデルにした学習用デモ群です。

> ⚠ **教育目的の簡略モデルです。** パラメータはすべて説明用の架空値で、
> 実際の細胞数・薬物動態・臨床成績を表すものではありません。

## 構成 / Modules

| File | 内容 |
|---|---|
| `glucose_insulin.py` | 共有コア。血糖-インスリン最小モデル (RK4)。β細胞量で健常/T1D/移植後を比較 |
| `differentiation.py` | 幹細胞→β細胞の多段階分化。段階収率・最終純度・1回投与に要する細胞数 |
| `graft_survival.py` | 移植片の生着と生存。IBMIR・自己免疫再燃・免疫回避3戦略の比較 |
| `closed_loop.py` | 転帰。24時間の血糖コントロールをポンプ vs 移植 vs 健常で比較 (TIR/A1c) |

## 実行 / Run

```bash
python stemcell_islet/glucose_insulin.py   # 血糖応答の基本
python stemcell_islet/differentiation.py   # 分化収率と純度
python stemcell_islet/graft_survival.py    # 移植片の長期生存
python stemcell_islet/closed_loop.py       # 1日の血糖管理の比較
```

外部ライブラリ不要 (標準ライブラリのみ)。`differentiation` 以外は
`glucose_insulin` を import するため、`stemcell_islet/` をカレントに実行してください。

## 治療の3つの壁とモデルの対応 / Three hurdles

1. **細胞をどう作るか** (`differentiation.py`) — 幹細胞を確実に成熟β細胞へ分化させる。
   後段の歩留まりと純度 (奇形腫リスクとなる未分化細胞の除去) が課題。
2. **移植片をどう生かすか** (`graft_survival.py`) — T1D は自己免疫疾患なので移植β細胞も
   攻撃される。免疫抑制・カプセル化・遺伝子編集ハイポイミューン化のトレードオフ。
3. **血糖をどう治すか** (`glucose_insulin.py`, `closed_loop.py`) — 血糖応答性の
   β細胞は、インスリン注射では届かない「生物学的閉ループ」を実現する。

これらを解けば、外因性インスリンに依存しない**根治に近い治療**が視野に入る、
というのが幹細胞由来膵島の狙いです。
