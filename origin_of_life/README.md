# 生命の起源 / The origin of life

生命がどのように無生物から立ち上がったのか (abiogenesis) をめぐる主要な
計算アイデアを、標準ライブラリだけで動くモデルにした学習用デモ群です。
「代謝の起源」「情報の起源」「区画の起源」「掌性の起源」という4つの問いを、
それぞれ動くシミュレーションとして実装します。

> ⚠ **教育目的の簡略モデルです。** パラメータは説明用の設定で、実際の
> 前生物的化学の速度や濃度を表すものではありません。

## 構成 / Modules

| File | 内容 | 問い |
|---|---|---|
| `kinetics.py` | 共有コア。RK4 積分器と自己触媒成長 (自己複製の芽) | — |
| `autocatalytic_sets.py` | Kauffman の自己触媒集合 (RAF) と相転移 | 代謝の起源 |
| `quasispecies.py` | Eigen の誤り破局と複製忠実度の限界 | 情報の起源 |
| `protocells.py` | 原始細胞と多段階選択 (区画化が協力を救う) | 区画の起源 |
| `homochirality.py` | Frank の自発的対称性の破れ (片方の掌性) | 掌性の起源 |

## 実行 / Run

```bash
python origin_of_life/kinetics.py             # 自己複製の芽 (自己触媒成長)
python origin_of_life/autocatalytic_sets.py    # 自己触媒集合 (RAF)
python origin_of_life/quasispecies.py          # 誤り破局
python origin_of_life/protocells.py            # 原始細胞と多段階選択
python origin_of_life/homochirality.py         # 対称性の破れ
```

外部ライブラリ不要 (標準ライブラリのみ)。`homochirality` は `kinetics` を
import するため、`origin_of_life/` をカレントに実行してください。

## 生命への4つの跳躍 / Four transitions toward life

1. **代謝の起源** (`autocatalytic_sets.py`) — 分子あたりの触媒数が閾値を超えると、
   互いを作り合う反応の閉じた輪 (RAF) が突然出現する。遺伝子なしに集団的自己触媒が
   『無料で』生じうる (代謝優先仮説)。
2. **情報の起源** (`quasispecies.py`) — 複製できても、忠実度が低ければ長い情報は
   保てない (誤り破局)。「長いゲノムには酵素が要り、酵素にはゲノムが要る」という
   Eigen のパラドックスが複雑化の壁になる。
3. **区画の起源** (`protocells.py`) — 膜で仕切ると、細胞内では負ける協力的な複製子が、
   細胞間の選択で守られる。区画化が分子の利害を『細胞』という単位にそろえる。
4. **掌性の起源** (`homochirality.py`) — 自己触媒 + 相互拮抗があれば、左右対称な状態は
   不安定になり、微小な揺らぎが増幅されて片方の鏡像体だけが残る。

**生命の起源に単一のシナリオはまだない。** これらは競合しつつ補完し合う断片であり、
自己触媒・複製・区画・対称性の破れがどう統合されて最初の細胞に至ったのかが、
今も開かれた問いです。
