# Patterns — 壊れない状態遷移 / Safe State Transitions

「例外・クラッシュ・同時実行が割り込んでも、データが壊れた中間状態にならない」
ためのパターン集です。核となる原則は 1 つ：

> 失敗しうる仕事はすべて**脇のコピー**の上でやり、本物への反映は
> **失敗しようがない一撃**（コミット）だけにする。

Build the new state off to the side (this part may fail), then commit with a
single operation that cannot fail.

## ファイル / Files

| File | Topic |
|---|---|
| [atomic_refill_demo.py](atomic_refill_demo.py) | コンテナの中身の入れ替え — スライス代入、clear+再投入の罠（遅延ジェネレータ・途中例外）、「完成させてから入れる」 |
| [atomic_file_write_demo.py](atomic_file_write_demo.py) | ファイルのアトミック書き換え — 一時ファイル + `os.replace()`、`tempfile.mkstemp` + `os.fdopen` |
| [immutability_demo.py](immutability_demo.py) | 不変性 — frozen dataclass、浅い不変性の罠、不変な「値」+ 原子的に遷移する「状態」の統合例 |

## 原則の現れ方 / One Principle, Many Forms

| 対象 | 準備（失敗してよい） | コミット（一撃） |
|---|---|---|
| `list` | 新リストを構築 | `lst[:] = new`（スライス代入） |
| `deque` / `dict` / `set` | `new = list(gen)` で実体化 | `clear()` + `extend()` / `update()` |
| ファイル | 同じディレクトリの一時ファイルに書き切る | `os.replace(tmp, path)` |
| オブジェクトの状態 | コピーを変更・検証 | `self._state = new`（参照の付け替え） |
| データベース | トランザクション内で変更 | `COMMIT` |

## 設計指針 / Design Guideline

1. **まず不変にできないか考える** — 小さな「値」（設定、座標、ID、レコード）は
   `@dataclass(frozen=True)` や `NamedTuple` で不変に。不正な値は生成時に拒否し、
   「存在すらさせない」。不変性は中身まで貫くこと（`list`→`tuple` など）。
2. **大きな「状態」は可変のまま、遷移を原子的に** — copy → 検証 → swap。
   変更経路を 1 本に絞り、外部には読み取り専用の窓（`MappingProxyType`）だけ見せる。
3. **コミットを一撃にできないときはロールバック** — 開始時にスナップショットを
   取り、失敗したら巻き戻す（データベースの ROLLBACK と同じ考え方）。
