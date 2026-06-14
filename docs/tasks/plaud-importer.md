# タスクリスト: plaud-importer MVP

**最終更新**: 2026-06-14  
**ステータス**: 未着手  
**対応仕様**: [docs/specs/plaud-importer.md](../specs/plaud-importer.md)

---

## フェーズ 1: プロジェクト基盤

- [ ] **1-1** `pyproject.toml` を作成する（python-dotenv 依存、pytest・ruff を dev deps）
- [ ] **1-2** `life_analytics/__init__.py` を作成する
- [ ] **1-3** `tests/__init__.py` を作成する
- [ ] **1-4** `.env.example` に `OBSIDIAN_VAULT_PATH` / `PLAUD_CLI` / `LOG_LEVEL` を追加する
- [ ] **1-5** `.gitignore` に `.env` が含まれていることを確認する

---

## フェーズ 2: Plaud CLI の出力フォーマット確認（実装前の調査）

- [ ] **2-1** `npx @plaud-ai/cli recent --days 2` を実行し、stdout の JSON 構造を確認する
  - 確認ポイント: フィールド名、日時フォーマット（ISO 8601？タイムゾーン付き？）、配列 or オブジェクト
- [ ] **2-2** `npx @plaud-ai/cli summary <file_id>` を実行し、出力フォーマットを確認する
  - 確認ポイント: プレーンテキスト / JSON / Markdown のどれか
- [ ] **2-3** 調査結果を `docs/specs/plaud-importer.md` の「要注意点」セクションに記録する

> ⚠️ フェーズ 3 の実装はこの調査完了後に開始する。

---

## フェーズ 3: コアモジュール実装

### 3-A: config.py

- [ ] **3-A-1** `Config` dataclass を実装する（vault_path, plaud_cli, log_level）
- [ ] **3-A-2** `load_config()` 関数を実装する（python-dotenv でロード、OBSIDIAN_VAULT_PATH 未設定時は ValueError）

### 3-B: plaud_client.py

- [ ] **3-B-1** `PlaudRecording` dataclass を実装する
- [ ] **3-B-2** `PlaudClient.__init__` を実装する（cli コマンドを受け取る）
- [ ] **3-B-3** `fetch_recordings(target_date)` を実装する
  - CLI 実行 → JSON パース → `start_at.date() == target_date` フィルタ
- [ ] **3-B-4** `fetch_summary(file_id)` を実装する
  - 失敗時は空文字列を返す（例外を飲み込む）
- [ ] **3-B-5** `format_duration(ms)` ユーティリティ関数を実装する

### 3-C: obsidian_writer.py

- [ ] **3-C-1** `ObsidianWriter.__init__` を実装する（vault_path を受け取る）
- [ ] **3-C-2** `_daily_note_path(date)` を実装する
- [ ] **3-C-3** `_ensure_daily_note(date)` を実装する（存在しなければ空ファイル作成）
- [ ] **3-C-4** `_ensure_plaud_section(note_path)` を実装する（`## Plaud` がなければ末尾に追加）
- [ ] **3-C-5** `_is_already_imported(note_path, recording_id)` を実装する（`<!-- plaud:{id} -->` の存在チェック）
- [ ] **3-C-6** `append_idea_to_daily_note(recording, summary, date)` を実装する
- [ ] **3-C-7** `_note_filename(recording, date)` を実装する（ファイル名サニタイズ）
- [ ] **3-C-8** `create_standalone_note(recording, summary, date)` を実装する
- [ ] **3-C-9** `append_link_to_daily_note(recording, note_path, date)` を実装する
- [ ] **3-C-10** `process_recording(recording, summary, date)` を実装する（ルーティングと委譲）

---

## フェーズ 4: CLI エントリーポイント

- [ ] **4-1** `plaud_importer.py` の `parse_args()` を実装する（`--date` 引数）
- [ ] **4-2** `setup_logging(level)` を実装する（stderr ハンドラ）
- [ ] **4-3** `main()` のオーケストレーションを実装する
- [ ] **4-4** `python -m life_analytics.plaud_importer --date 2026-06-14` で手動実行できることを確認する

---

## フェーズ 5: テスト

- [ ] **5-1** `test_plaud_client.py`: `subprocess.run` をモックして `fetch_recordings` の JSON パース・日付フィルタをテストする
- [ ] **5-2** `test_plaud_client.py`: `fetch_summary` の失敗時（空文字列返却）をテストする
- [ ] **5-3** `test_obsidian_writer.py`: `tmp_path` を使って Daily Note 新規作成をテストする
- [ ] **5-4** `test_obsidian_writer.py`: IDEA_ エントリの追記・冪等性をテストする
- [ ] **5-5** `test_obsidian_writer.py`: 単独ノートの作成・重複スキップをテストする
- [ ] **5-6** `test_obsidian_writer.py`: Daily Note へのリンク追記をテストする
- [ ] **5-7** `test_plaud_importer.py`: `--date` 引数パースをテストする
- [ ] **5-8** `test_plaud_importer.py`: 全体オーケストレーション（PlaudClient・ObsidianWriter をモック）をテストする

---

## フェーズ 6: ドキュメント整備

- [ ] **6-1** `CLAUDE.md` のプレースホルダーをこのプロジェクト向けに記入する
- [ ] **6-2** `docs/product-requirements.md` を plaud-importer の内容で更新する
- [ ] **6-3** `docs/architecture.md` にモジュール構成を記入する
- [ ] **6-4** `README.md` にセットアップ手順（uv sync, .env 設定, cron 設定例）を追記する

---

## 完了条件

- `ruff check .` / `ruff format --check .` が通る
- `pytest` が全テスト GREEN
- `python -m life_analytics.plaud_importer --date 2026-06-14` を実際の Vault パスで実行し、Daily Note と Notes/PLAUD/ へ期待通り書き込まれることを手動確認する
- 同じコマンドを再実行してもファイルが破壊されない（冪等性確認）
