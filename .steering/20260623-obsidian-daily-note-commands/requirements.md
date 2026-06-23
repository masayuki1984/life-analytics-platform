# 要件定義: obsidian-daily-note-commands

**作成日**: 2026-06-23  
**担当**: masayuki1984

---

## 概要

Obsidian の Daily Note を自動管理するための2つの独立したコマンドを追加する。
1つ目は今日の Daily Note をテンプレートから作成するコマンド、
2つ目は前日の Daily Note に Plaud 録音ノートのリンクを追記するコマンド。

## スコープ

### IN（実装する）

- `python -m life_analytics.obsidian.create_daily_note` — Daily Note 作成コマンド
- `python -m life_analytics.obsidian.append_plaud_link` — Plaud リンク追記コマンド
- `--date YYYY-MM-DD` オプション（将来テスト容易性のため）
- ユニットテスト
- `.env.example` への `OBSIDIAN_VAULT_ROOT` 追加

### OUT（実装しない）

- launchd plist の作成・設定
- 既存 `config.py` / `ObsidianWriter` の変更
- `OBSIDIAN_VAULT_PATH` と `OBSIDIAN_VAULT_ROOT` の統合

## 機能要件

### 1. Daily Note 作成コマンド（`create_daily_note`）

- 実行時点の Asia/Tokyo の今日の日付で Daily Note を作成する
- `--date YYYY-MM-DD` 指定時はその日付を使用する
- 保存先: `${OBSIDIAN_VAULT_ROOT}/Daily/YYYY/MM/YYYY-MM-DD.md`
- テンプレート: `${OBSIDIAN_VAULT_ROOT}/Templates/daily.md`
- 対象ファイルが既に存在する場合は何もせず正常終了（冪等）
- 対象ディレクトリが存在しない場合は作成する
- `OBSIDIAN_VAULT_ROOT` 未設定 → エラーで異常終了
- テンプレートファイルが存在しない → エラーで異常終了

### 2. Plaud リンク追記コマンド（`append_plaud_link`）

- デフォルトは Asia/Tokyo の前日の日付を対象にする
- `--date YYYY-MM-DD` 指定時はその日付を対象にする
- 対象 Daily Note が存在しない場合はスキップして正常終了
- `## Plaud` セクションが存在しない場合はスキップして正常終了
- `${OBSIDIAN_VAULT_ROOT}/Notes/PLAUD/YYYY-MM-DD-*.md` を収集してリンク生成
- 既に同じリンクが存在する場合は重複追記しない（冪等）
- リンクを `## Plaud` セクション内（次の `##` の前）に挿入する

### データ要件

- **入力**: `OBSIDIAN_VAULT_ROOT` 環境変数、`Templates/daily.md`、`Notes/PLAUD/` 内の Plaud ノートファイル
- **出力**: `Daily/YYYY/MM/YYYY-MM-DD.md`（作成・更新）
- **保存先**: Obsidian Vault 内ファイルシステム

## 非機能要件

- **パフォーマンス**: ファイル操作のみ。数秒以内に完了
- **エラーハンドリング**: 異常終了は `sys.exit(1)`、正常終了は `sys.exit(0)`
- **ログ**: `logging` モジュールを使用。「作成した」「既に存在するためスキップ」「対象Daily Noteなしでスキップ」「Plaudセクションなしでスキップ」が分かる

## 受け入れ条件

- [ ] `create_daily_note` がテンプレートをコピーして Daily Note を作成できる
- [ ] `create_daily_note` は既存ファイルを上書きしない
- [ ] `create_daily_note` はテンプレート未存在時に異常終了する
- [ ] `append_plaud_link` が `## Plaud` セクション内にリンクを挿入できる
- [ ] `append_plaud_link` は Daily Note 未存在時に正常終了する
- [ ] `append_plaud_link` は `## Plaud` セクション未存在時に正常終了する
- [ ] `append_plaud_link` は重複リンクを追記しない（冪等）
- [ ] `--date` オプションで任意の日付を指定できる
- [ ] ユニットテストが全て通る
