# AGENTS.md

このリポジトリでコーディングエージェント (Claude Code など) が作業するときのガイドです。
Guidance for coding agents working in this repository.

## プロジェクト概要 / Overview

Python の学習・参照用サンプル集です。アプリケーションではなく、
「読んで理解する」「単体で実行して動きを確かめる」ための独立したスクリプト群です。

- **外部依存なし** — 標準ライブラリのみ。`requirements.txt` も仮想環境も追加しないでください。
- **Python 3.11+** を前提 (`match`/`case`、`zoneinfo`、`list[str]` などの組み込みジェネリクスを使用)。
- 各ファイルは自己完結。モジュール間の `import` は行いません。

## ディレクトリ構成 / Layout

| Directory | 役割 | スタイル |
|---|---|---|
| `basics/` | 文法解説 (data types, control flow, functions, comprehensions) | トップレベルで `print` するデモスクリプト |
| `data_structures/` | Stack, Queue, LinkedList, BST | クラス定義 + `if __name__ == "__main__":` デモ |
| `utilities/` | ファイル/文字列/日時ヘルパー | 関数定義 + `if __name__ == "__main__":` デモ |
| `standard_library/` | collections, itertools, pathlib の使用例 | トップレベルで `print` するデモスクリプト |

新しいファイルを追加する際は、そのディレクトリの既存スタイルに合わせてください。
`README.md` の構成表も忘れずに更新します。

## 実行と確認 / Running and verifying

テストフレームワーク、リンター設定、CI はありません。**検証方法は「実際に実行すること」です。**

```bash
python3 basics/data_types.py
python3 data_structures/binary_tree.py
python3 utilities/string_utils.py
```

変更したファイル (と、影響を受けうるファイル) を必ず実行し、例外なく最後まで
出力が出ることを確認してからコミットしてください。

## コーディング規約 / Conventions

既存コードを読めばわかる通りですが、明文化しておきます。

- **モジュール docstring** をファイル先頭に必ず置く。1〜2 行、内容の要約。
- **セクション区切り**は罫線コメントで統一:
  ```python
  # ── Section name ──────────────────────────────────────────────────────────
  ```
  行はおおむね 78 桁で揃えます。
- **コメント・docstring は英語**、`README.md` と本ファイルは日英併記。
- **型ヒント**は公開関数・メソッドのシグネチャに付ける (`def slugify(text: str) -> str:`)。
  デモ用のトップレベル変数は任意 (`x: int = 42` のように教材として書く場合もあり)。
- 相互参照する型を書く場合は `from __future__ import annotations` を使う
  (`data_structures/binary_tree.py` 参照)。
- 文字列整形は **f-string**。`%` や `.format()` は使わない。
- 内部状態は `_data` のようにアンダースコア接頭辞。`__repr__` を用意する。
- エラーは適切な組み込み例外で送出 (空スタックの `pop` → `IndexError` など)。
- 連続する代入は視認性のため縦に揃えることがあります (`cwd  = ...` / `home = ...`)。既存の揃えを壊さないこと。
- インデントは半角スペース 4、フォーマッタは未導入なので `black` などを一括適用しないでください
  (上記の桁揃えが崩れます)。

## コミット / Commits

Conventional Commits 形式、命令形・小文字始まりの 1 行サマリ:

```
feat: add binary heap implementation
docs: clarify how to run utility modules
fix: handle empty input in slugify
```

作業ブランチにコミットし、明示的に依頼されない限り Pull Request は作成しません。
