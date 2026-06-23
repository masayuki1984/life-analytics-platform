# タスクリスト: obsidian-daily-note-commands

**作成日**: 2026-06-23  
**ステータス**: 完了

---

## タスク

<!-- [ ] 未完了  [x] 完了  [~] スキップ（理由を記載） -->

### セットアップ

- [x] `life_analytics/obsidian/` パッケージディレクトリと `__init__.py` を作成する
- [x] `.env` と `.env.example` に `OBSIDIAN_VAULT_ROOT` を追加する

### コア実装

- [x] `life_analytics/obsidian/create_daily_note.py` を実装する
  - `load_vault_root()` — 環境変数読み込み
  - `get_daily_note_path()` — パス生成
  - `get_template_content()` — テンプレート読み込み（未存在時エラー）
  - `create_daily_note()` — 冪等作成ロジック
  - `main()` — argparse + ロギング設定
- [x] `life_analytics/obsidian/append_plaud_link.py` を実装する
  - `PlaudNoteInfo` dataclass
  - `parse_plaud_note()` — frontmatter + 見出しパーサー
  - `collect_plaud_notes()` — 日付別収集
  - `format_link_entry()` — リンクエントリ生成
  - `append_to_plaud_section()` — セクション内挿入ロジック
  - `append_plaud_link()` — メインロジック（冪等）
  - `main()` — argparse + ロギング設定

### テスト

- [x] `tests/test_create_daily_note.py` を作成する
  - テンプレートからの作成
  - 既存ファイルのスキップ
  - ディレクトリ自動作成
  - テンプレート未存在時のエラー
  - `--date` フラグの動作
- [x] `tests/test_append_plaud_link.py` を作成する
  - `## Plaud` セクションへのリンク挿入
  - Daily Note 未存在時のスキップ
  - `## Plaud` セクション未存在時のスキップ
  - 重複リンクの非追記（冪等）
  - `append_to_plaud_section()` の各エッジケース
- [x] テストが全て通ることを確認する（`uv run pytest`）

### 動作確認

- [x] `ruff check` / `ruff format` でリント・フォーマットが通ることを確認する

### バグ修正: obsidian_writer のセクション末尾追記問題

**背景**: Daily Note テンプレートに `## Plaud` の後続セクション（`## Ideas` 等）がある場合、
既存の `obsidian_writer.py` が `open(file, "a")` でファイル末尾に追記するため、
リンクが `## Plaud` セクション内ではなくファイル末尾に追加されてしまう。

- [x] `obsidian_writer.py` に `_insert_into_plaud_section()` ヘルパーを追加する
- [x] `_process_idea()` を `open("a")` からセクション内挿入に変更する
- [x] `_append_link_if_missing()` を `open("a")` からセクション内挿入に変更する
- [x] `write_no_recordings()` を `open("a")` からセクション内挿入に変更する
- [x] 既存テストが全て通ることを確認する（`uv run pytest`）
- [x] `## Plaud` が中間セクションにある場合のテストを `test_obsidian_writer.py` に追加する

---

## スキップ記録

<!-- スキップしたタスクがあればここに理由を記録 -->

---

## 振り返り

<!-- 全タスク完了後に記載 -->

### 予想外だったこと

-

### 次回への学び

-

### 残タスク・技術的負債

- `obsidian_writer.py` の `open("a")` パターンは Daily Note テンプレートに後続セクションがある場合に壊れる。`_insert_into_plaud_section()` ヘルパーで修正予定
