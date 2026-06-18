# 技術設計: plaud-importer

**作成日**: 2026-06-14

> 詳細設計は [docs/specs/plaud-importer.md](../../docs/specs/plaud-importer.md) を参照。
> このファイルはセッション用サマリ。

---

## アーキテクチャ概要

```
CLI (plaud_importer.py)
  ├── PlaudClient (plaud_client.py)
  │     ├── npx @plaud-ai/cli recent --days N  → JSON パース → 日付フィルタ
  │     └── npx @plaud-ai/cli summary <id>     → str
  └── ObsidianWriter (obsidian_writer.py)
        ├── IDEA_   → Daily Note に直接追記
        └── その他  → Notes/PLAUD/ に単独ノート作成 + Daily Note にリンク
```

## ファイル構成

```
life_analytics/
├── __init__.py
├── config.py              # 環境変数ロード (OBSIDIAN_VAULT_PATH 等)
├── plaud_client.py        # Plaud CLI サブプロセスラッパー
├── obsidian_writer.py     # Obsidian ファイル書き込み
└── plaud_importer.py      # CLI エントリーポイント

tests/
├── __init__.py
├── test_plaud_client.py
├── test_obsidian_writer.py
└── test_plaud_importer.py

pyproject.toml
```

## dry-run 設計

`ObsidianWriter` に `dry_run: bool` フラグを持たせる。
`True` の場合、ファイル書き込みを実行せず `[DRY-RUN]` プレフィックス付きでログ出力する。

## Plaud CLI 出力フォーマット（調査済み 2026-06-14）

**JSON オプションなし。すべてテキスト形式。**

### `recent --days N` 出力
```
- Fetching recordings from the last 2 days...

Recordings in the last 2 days: 1

  7190240c21240ccfc5c38038e42c893e  2026-06-14 18:48:29テストメモ  2026-06-14  16s
```
→ 各行から 32 文字の hex ID を regex 抽出し、`file <id>` で詳細取得

### `file <id>` 出力
```
  id:           7190240c21240ccfc5c38038e42c893e
  name:         2026-06-14 18:48:29テストメモ
  created_at:   2026-06-14T09:49:01
  start_at:     2026-06-14T09:48:29
  duration:     16s
```
→ `key: value` 形式でパース。`start_at` はタイムゾーンなし ISO 8601。`duration` は整形済み文字列。

### `summary <id>` 出力
```
- Fetching summary...

Summary: 2026-06-14 18:48:29テストメモ

原文の音声書き起こし内容は以下の通りです：
> [Speaker 1]これはテストの録音です。
```
→ `Summary: {name}` 行の次の空行以降を本文として抽出

## 設計変更点（調査後）

- `duration` は CLI から整形済み文字列で返るため `format_duration()` は不要
- `start_at` はタイムゾーンなし → naive datetime としてそのまま比較

## 懸念事項・リスク

- 録音件数が多い場合、`file <id>` の呼び出しが録音件数分になる（MVP では許容）
- `summary` がない録音（処理中等）はスキップしてログに記録する
