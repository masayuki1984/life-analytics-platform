# タスクリスト: plaud-importer

**作成日**: 2026-06-14  
**ステータス**: 進行中

---

## タスク

<!-- [ ] 未完了  [x] 完了  [~] スキップ（理由を記載） -->

### フェーズ 1: プロジェクト基盤

- [x] 1-1: `pyproject.toml` を作成する（python-dotenv, pytest, ruff）
- [x] 1-2: `life_analytics/__init__.py` を作成する
- [x] 1-3: `tests/__init__.py` を作成する
- [x] 1-4: `.env.example` に Obsidian / Plaud 設定項目を追加する
- [x] 1-5: `.gitignore` に `.env` が含まれていることを確認する

### フェーズ 2: Plaud CLI 出力フォーマット調査

- [x] 2-1: `npx @plaud-ai/cli recent --days 2` を実行して出力構造を確認する
- [x] 2-2: `npx @plaud-ai/cli summary <file_id>` を実行して出力形式を確認する

### フェーズ 3: コアモジュール実装

- [x] 3-1: `config.py` — Config dataclass + load_config()
- [x] 3-2: `plaud_client.py` — PlaudRecording dataclass
- [x] 3-3: `plaud_client.py` — PlaudClient.fetch_recordings()
- [x] 3-4: `plaud_client.py` — PlaudClient.fetch_summary()
- [~] 3-5: `plaud_client.py` — format_duration() ユーティリティ（CLI が整形済み文字列を返すため不要）
- [x] 3-6: `obsidian_writer.py` — ObsidianWriter 基盤（__init__, dry_run, _daily_note_path）
- [x] 3-7: `obsidian_writer.py` — _ensure_daily_note, _ensure_plaud_section
- [x] 3-8: `obsidian_writer.py` — _is_already_imported
- [x] 3-9: `obsidian_writer.py` — append_idea_to_daily_note
- [x] 3-10: `obsidian_writer.py` — create_standalone_note + _note_filename
- [x] 3-11: `obsidian_writer.py` — append_link_to_daily_note
- [x] 3-12: `obsidian_writer.py` — process_recording（ルーティング）

### フェーズ 4: CLI エントリーポイント

- [x] 4-1: `plaud_importer.py` — parse_args()（--date, --dry-run）
- [x] 4-2: `plaud_importer.py` — setup_logging()
- [x] 4-3: `plaud_importer.py` — main() オーケストレーション

### フェーズ 5: テスト

- [x] 5-1: `test_plaud_client.py` — fetch_recordings の JSON パース・日付フィルタ
- [x] 5-2: `test_plaud_client.py` — fetch_summary 失敗時の空文字列返却
- [x] 5-3: `test_obsidian_writer.py` — Daily Note 新規作成
- [x] 5-4: `test_obsidian_writer.py` — IDEA_ 追記・冪等性
- [x] 5-5: `test_obsidian_writer.py` — 単独ノート作成・重複スキップ
- [x] 5-6: `test_obsidian_writer.py` — Daily Note リンク追記
- [x] 5-7: `test_plaud_importer.py` — --date / --dry-run 引数パース
- [x] 5-8: pytest 全 GREEN 確認（30/30）

### フェーズ 6: ドキュメント・最終確認

- [x] 6-1: `README.md` にセットアップ手順と cron 設定例を追記する
- [x] 6-2: `ruff check .` / `ruff format --check .` が通ることを確認する
- [x] 6-3: `--dry-run` での動作を手動確認する（1 件 created、ファイル未生成を確認）

---

## スキップ記録

<!-- スキップしたタスクがあればここに理由を記録 -->

---

## 振り返り

<!-- 全タスク完了後に記載 -->

### 予想外だったこと

- Plaud CLI に JSON 出力オプションがなく、テキストパースが必要だった。`recent` 出力のパース方式を「ID 抽出 → `file <id>` で詳細取得」の 2 ステップに変更した
- `duration` フィールドが CLI から整形済み文字列で返るため、仕様で予定していた `format_duration()` が不要だった
- dry_run モードで `notes_dir.mkdir()` と `path.parent.mkdir()` が実行されてしまいテストが 2 件失敗。dry_run ガードの抜け漏れは実装後のテストで初めて発覚した

### 次回への学び

- 外部 CLI を使う場合は、まず出力フォーマット調査をスモークテストとして実施してから設計を固める（今回は仕様後に調査したため設計変更が必要になった）
- dry_run フラグは「ファイル書き込み」だけでなく「ディレクトリ作成」も全て抑制する必要がある。副作用を持つ全ての箇所に dry_run ガードを追加するルールを徹底する
- hatchling + `pyproject.toml` でパッケージ名と `life_analytics` ディレクトリ名が一致しない場合は `[tool.hatch.build.targets.wheel] packages` の明示指定が必要

### 残タスク・技術的負債

- `CLAUDE.md` / `docs/product-requirements.md` / `docs/architecture.md` のプレースホルダーが未記入（フェーズ 6 の 6-1〜6-3 は意図的に次セッションへ先送り）
- 録音件数が多い場合に `file <id>` の呼び出しが N 回発生する（MVP では許容、将来的には `recent` 出力のみでフィルタできる形式確認が必要）
