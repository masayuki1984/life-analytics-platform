# タスクリスト: Daily Note テンプレート対応

**作成日**: 2026-06-22  
**ステータス**: 完了

---

## タスク

<!-- [ ] 未完了  [x] 完了  [~] スキップ（理由を記載） -->

### フェーズ 1: obsidian_writer.py

- [x] 1-1: `_ensure_daily_note()` でテンプレートパス (`vault_path / "Templates" / "daily.md"`) の存在を確認する
- [x] 1-2: テンプレートが存在する場合、内容を `write_text` でコピーして Daily Note を作成する
- [x] 1-3: テンプレートが存在しない場合、`logger.warning` を出して空ファイル (`touch`) で作成する
- [x] 1-4: `dry_run` 時はテンプレートの有無をログに記録するだけでファイルを作成しない
- [x] 1-5: `_is_no_recordings_written()` メソッドを追加する（ファイル全体で `録音なし` を検索）
- [x] 1-6: `write_no_recordings()` パブリックメソッドを追加する（冪等・`_ensure_plaud_section` 呼び出し含む）

### フェーズ 2: plaud_importer.py

- [x] 2-1: 録音 0 件の場合に `writer.write_no_recordings(target_date)` を呼ぶ

### フェーズ 3: テスト

- [x] 3-1: `test_obsidian_writer.py` — テンプレートが存在する場合、新規 Daily Note にテンプレート内容がコピーされる
- [x] 3-2: `test_obsidian_writer.py` — テンプレートが存在しない場合、空ファイルが作成される（WARNING ログあり）
- [x] 3-3: `test_obsidian_writer.py` — 既存 Daily Note がある場合、テンプレートで上書きされない
- [x] 3-4: `test_obsidian_writer.py` — `write_no_recordings()` で Plaud セクションに `録音なし` が書き込まれる
- [x] 3-5: `test_obsidian_writer.py` — `## Plaud` セクションがない場合、末尾に追加してから `録音なし` を書き込む
- [x] 3-6: `test_obsidian_writer.py` — `write_no_recordings()` を 2 回呼んでも `録音なし` が重複しない
- [x] 3-7: `test_obsidian_writer.py` — `dry_run` 時に `write_no_recordings()` がファイルを作成・変更しない
- [x] 3-8: `test_plaud_importer.py` — 録音 0 件の場合に `write_no_recordings` が呼ばれることを確認する

### フェーズ 4: ドキュメント・最終確認

- [x] 4-1: `README.md` に `Templates/daily.md` を用意する手順を追記する
- [x] 4-2: `docs/specs/plaud-importer.md` の Daily Note 生成仕様を更新する
- [x] 4-3: `pytest` 全 GREEN を確認する（`test_main_exits_1_on_missing_env` は本 PR 以前からの既存失敗）
- [x] 4-4: `ruff check .` が通ることを確認する

---

## スキップ記録

<!-- スキップしたタスクがあればここに理由を記録 -->

---

## 振り返り

<!-- 全タスク完了後に記載 -->

### 予想外だったこと

- dry-run 時に `ensure_daily_note`（main から）と `write_no_recordings`（内部）が両方 `_ensure_daily_note` を呼ぶため、「Daily Note を作成します」ログが 2 回出力される。実行時はファイルが存在するため 2 回目はスキップされ問題ないが、dry-run では常に `path.exists() == False` となるため重複する
- ruff で日本語混じりのログ文字列が行長 100 を超えた。マルチバイト文字は見た目より長くなることを念頭に置く必要がある

### 次回への学び

- dry-run での二重ログを防ぐには、`write_no_recordings` が `_ensure_daily_note` を呼ばず、呼び出し元で取得したパスを引数として受け取る設計にするとよい。ただし API の変更が必要なため今回は許容した
- テンプレートの存在チェックを dry-run でも実ファイルを読んで判定したことで、ログの正確性（「テンプレート使用」か「空ファイル」かの表示）を保てた

### 残タスク・技術的負債

- dry-run 時の「Daily Note を作成します」ログが 2 回表示される（機能的には問題なし）
- `Templates/daily.md` が Vault に存在しない場合の WARNING が毎日出力される。README にセットアップ手順を記載したが、初回実行ガイダンスとして改善の余地がある
- テンプレート内の変数展開（`{{date}}` 等）は対象外。将来的に必要になれば `Config` にテンプレートパスを追加しつつ展開ロジックを実装する
