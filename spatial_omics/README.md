# 単一細胞空間オミクス / Single-cell spatial omics

組織内の細胞の**空間的な位置を保ったまま**遺伝子発現を測る単一細胞空間オミクス
(Visium, MERFISH, Xenium 等) の計算解析を、標準ライブラリだけで実装した
学習用デモ群です。合成組織 (腫瘍核・免疫浸潤・間質の3ドメイン) を生成し、
細胞型同定から空間統計・細胞間通信までの一連の解析を追えます。

> ⚠ **教育目的の合成データ・簡易実装です。** 実データの統計的性質を厳密に
> 再現するものではなく、既存ツール (Scanpy/Squidpy 等) の代替でもありません。

## 構成 / Modules

| File | 内容 |
|---|---|
| `synthetic_tissue.py` | 共有コア。空間座標・発現・細胞型・空間ドメインを持つ組織を生成、kNN 近傍グラフ |
| `clustering.py` | 発現による教師なしクラスタリング (k-means)、ARI 評価、マーカー遺伝子同定 |
| `spatial_stats.py` | 空間的変動遺伝子 (Moran's I)、近傍エンリッチメント (順列検定) |
| `cell_communication.py` | リガンド-受容体による細胞間通信 (発現 × 空間的隣接) |

## 実行 / Run

```bash
python spatial_omics/synthetic_tissue.py    # 組織の生成と空間マップ
python spatial_omics/clustering.py          # 細胞型のクラスタリング
python spatial_omics/spatial_stats.py       # Moran's I と近傍エンリッチメント
python spatial_omics/cell_communication.py  # リガンド-受容体通信
```

外部ライブラリ不要 (標準ライブラリのみ)。各モジュールは `synthetic_tissue` を
import するため、`spatial_omics/` をカレントに実行してください。

## 解析の流れと「空間」の価値 / Why spatial matters

1. **細胞型を知る** (`clustering.py`) — 発現プロファイルだけで細胞型はほぼ復元できる
   (ARI ≈ 0.93)。ここまでは通常の単一細胞 RNA-seq でも可能。
2. **どこにいるかを知る** (`spatial_stats.py`) — Moran's I で空間的に構造化した遺伝子を
   選び、近傍エンリッチメントでどの細胞型どうしが隣接するかを定量。ここからが空間固有。
3. **何を伝え合うかを知る** (`cell_communication.py`) — L-R が発現していても細胞が
   離れていれば通信は成立しない。「発現 × 空間的隣接」で初めて細胞間通信が読める。

細胞の**アイデンティティ**に**位置関係**を重ねることで、組織を「細胞の集合」から
「相互作用する社会」として読み解けるようになる、というのが空間オミクスの核心です。
