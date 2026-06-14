# 要件定義: plaud-importer

**最終更新**: 2026-06-14  
**ステータス**: 草案

---

## 背景と目的

Plaud デバイスで日中に録音した音声メモを、翌日 00:30 に自動で Obsidian SecondBrain へ取り込む。
録音後に Plaud アプリでタイトルのプレフィックスを手動編集することで、ノートの保存先を制御する運用を前提とする。

**解決する問題**: 録音→Obsidian への転記が現状手動であり、継続的な運用の障壁になっている。

---

## スコープ（MVP）

### 対象

- 前日分の Plaud 録音を Obsidian に自動インポートする CLI ツール
- `python -m life_analytics.plaud_importer [--date YYYY-MM-DD]`

### 対象外

- 文字起こし（transcript）の取得・保存（要約 summary のみ）
- タグ・フォルダ情報（Plaud CLI で取得不可）
- cron ジョブの自動セットアップ（ユーザーが手動で設定）
- 既存ノートへの差分マージ（上書き / スキップで対応）

---

## 機能要件

### FR1: 処理対象日の指定

- `--date YYYY-MM-DD` 引数で対象日を指定できる
- 省略時はスクリプト実行日の前日（昨日）をデフォルトとする

### FR2: Plaud 録音の取得

- 指定日に `start_at` が一致する録音を全件取得する
- 取得に使う Plaud CLI コマンド: `npx @plaud-ai/cli recent --days N`（N は対象日からの経過日数 + 2）
- 各録音について `summary` を追加取得する（`npx @plaud-ai/cli summary <file_id>`）

### FR3: タイトルプレフィックスによるルーティング

| プレフィックス | 処理 |
|---|---|
| `IDEA_` | Daily Note の Plaud セクションに直接追記 |
| `MEETING_` | `Notes/PLAUD/` に単独ノート作成 → Daily Note にリンク追記 |
| `SEMINAR_` | 同上 |
| `STUDY_` | 同上 |
| プレフィックスなし | 同上 |

### FR4: Daily Note への追記

- Daily Note が存在しない場合は新規作成する
- Daily Note パス: `Daily/YYYY/MM/YYYY-MM-DD.md`（Vault ルートからの相対パス）
- Plaud セクション見出し `## Plaud` がなければ末尾に追加する
- セクション内に各録音のエントリを追記する

### FR5: 単独ノートの作成（IDEA_ 以外）

- 保存先: `Notes/PLAUD/{date}-{sanitized_name}.md`
- ファイルが既存の場合はスキップしてログに記録する（上書きしない）

### FR6: Daily Note へのリンク追記（単独ノート作成後）

- `## Plaud` セクション内に Obsidian WikiLink 形式でリンクを追記する
- 既にリンクが存在する場合はスキップする

### FR7: 冪等性

- 同じ日付で再実行しても既存コンテンツを破壊しない
- 既にインポート済みのエントリはスキップする

---

## 非機能要件

### NF1: 終了コード

| 状況 | exit code |
|---|---|
| 全録音の処理に成功 | 0 |
| 一部録音のスキップ（ファイル既存等） | 0 |
| 致命的エラー（Plaud CLI が見つからない、Vault パス不正等） | 1 |

### NF2: ログ

- stderr にログを出力する
- LOG_LEVEL 環境変数で制御（デフォルト: INFO）
- 各録音の処理結果（created / skipped / failed）を INFO レベルで記録する

### NF3: 設定

- `OBSIDIAN_VAULT_PATH`: Vault の絶対パス（必須）
- `PLAUD_CLI`: Plaud CLI コマンド（任意、デフォルト: `npx @plaud-ai/cli`）
- `LOG_LEVEL`: ログレベル（任意、デフォルト: `INFO`）

### NF4: 実行環境

- Python 3.12 以上
- Node.js / npx が PATH に存在すること（Plaud CLI の実行に必要）
- cron または launchd での定期実行を想定（00:30 に前日分を処理）

---

## 運用フロー

```
[Plaud デバイスで録音]
      ↓
[Plaud アプリでタイトルにプレフィックスを付けて編集]
      ↓
[00:30 に cron が plaud_importer を実行]
      ↓
[Obsidian SecondBrain に自動追記]
```

---

## バックログ（MVP 以降）

- 文字起こし（transcript）の取得・保存
- 既存 Daily Note の Plaud セクション内でのエントリ更新（差分マージ）
- 処理結果の通知（Discord Webhook 等）
- 複数日まとめて再処理するバッチモード（`--from` / `--to` 引数）
