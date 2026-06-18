# 要件定義: plaud-importer

**作成日**: 2026-06-14

> 詳細要件は [docs/requirements/plaud-importer.md](../../docs/requirements/plaud-importer.md) を参照。
> このファイルはセッション用サマリ。

---

## 概要

Plaud CLI から前日分の録音要約を取得し、タイトルプレフィックスに応じて
Obsidian SecondBrain の Daily Note と Notes/PLAUD/ に Markdown 出力する CLI ツール。

## スコープ

### IN（実装する）

- Plaud CLI で前日分録音を取得（`recent --days N` → 日付フィルタ）
- 録音 ID ごとに `file` / `summary` を取得
- タイトルプレフィックスで分類（`IDEA_` → Daily Note 直接追記、それ以外 → 単独ノート + リンク）
- Obsidian Daily Note への追記（存在しなければ新規作成）
- `Notes/PLAUD/` への単独ノート作成
- `--dry-run` モード（ファイル書き込みなしで処理内容を標準出力）
- 最低限の README 追記

### OUT（実装しない）

- 文字起こし（transcript）取得
- タグ・フォルダ情報の取得
- cron 自動セットアップ

## 受け入れ条件

- [ ] `python -m life_analytics.plaud_importer --date 2026-06-14` が動く
- [ ] `--dry-run` でファイルを書かずに処理内容が出力される
- [ ] 再実行しても既存コンテンツを破壊しない（冪等性）
- [ ] `pytest` が全 GREEN
- [ ] `ruff check .` が通る
