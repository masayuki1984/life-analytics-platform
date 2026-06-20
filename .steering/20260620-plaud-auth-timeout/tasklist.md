# タスクリスト: plaud-importer 認証エラー・タイムアウト対応

**作成日**: 2026-06-20  
**ステータス**: 完了

---

## タスク

<!-- [ ] 未完了  [x] 完了  [~] スキップ（理由を記載） -->

### フェーズ 1: config.py

- [x] 1-1: `Config` に `plaud_timeout: int` フィールドを追加する
- [x] 1-2: `load_config()` で `PLAUD_TIMEOUT` を読み取り、不正値は `ValueError` にする
- [x] 1-3: `.env.example` に `PLAUD_TIMEOUT` を追記する

### フェーズ 2: plaud_client.py

- [x] 2-1: `PlaudAuthenticationError(PlaudCLIError)` クラスを追加する
- [x] 2-2: `_AUTH_FAILED_RE` 正規表現定数を追加する
- [x] 2-3: `PlaudClient.__init__` に `timeout: int = 60` 引数を追加する
- [x] 2-4: `_run()` に DEBUG ログ（コマンド・開始時刻）を追加する
- [x] 2-5: `_run()` の `subprocess.run` に `timeout=self._timeout` を追加する
- [x] 2-6: `_run()` で `subprocess.TimeoutExpired` を `PlaudCLIError` に変換する
- [x] 2-7: `_run()` で AUTH_FAILED を検知して `PlaudAuthenticationError` を raise する
- [x] 2-8: `_run()` の `finally` ブロックに終了時刻・経過時間の DEBUG ログを追加する
- [x] 2-9: `fetch_summary()` で `PlaudAuthenticationError` を握りつぶさず再 raise する

### フェーズ 3: plaud_importer.py

- [x] 3-1: `PlaudAuthenticationError` を import する
- [x] 3-2: `PlaudClient` 生成時に `timeout=config.plaud_timeout` を渡す
- [x] 3-3: `fetch_recordings()` の例外ハンドリングに `PlaudAuthenticationError` を追加する
- [x] 3-4: `fetch_summary()` 呼び出しを `try/except PlaudAuthenticationError` で囲む

### フェーズ 4: テスト

- [x] 4-1: `test_plaud_client.py` — AUTH_FAILED を含む stdout で `PlaudAuthenticationError` が raise されることを確認する
- [x] 4-2: `test_plaud_client.py` — AUTH_FAILED を含む stderr で `PlaudAuthenticationError` が raise されることを確認する
- [x] 4-3: `test_plaud_client.py` — `TimeoutExpired` が `PlaudCLIError` に変換されることを確認する
- [x] 4-4: `test_plaud_client.py` — 正常系: timeout 付きの `PlaudClient` が録音を取得できることを確認する
- [x] 4-5: `test_plaud_importer.py` — `fetch_recordings` が `PlaudAuthenticationError` を raise したとき `main()` が exit 1 することを確認する

### フェーズ 5: ドキュメント・最終確認

- [x] 5-1: `README.md` にログイン手順（`plaud login` コマンド）を追記する
- [x] 5-2: `README.md` にトークン切れ時の復旧手順を追記する
- [x] 5-3: `pytest` 全 GREEN を確認する（`test_main_exits_1_on_missing_env` は本 PR 以前からの既存失敗）
- [x] 5-4: `ruff check .` が通ることを確認する

---

## スキップ記録

<!-- スキップしたタスクがあればここに理由を記録 -->

---

## 振り返り

<!-- 全タスク完了後に記載 -->

### 予想外だったこと

- `fetch_recordings()` のループ内にある `except PlaudCLIError` が `PlaudAuthenticationError` も飲み込んでしまうため、ループ内に `except PlaudAuthenticationError: raise` を明示的に追加する必要があった。サブクラス設計と既存の例外ハンドリングの干渉は設計時に見落としやすい
- テストの `_mock_subprocess` ヘルパー内に `import subprocess` を書いたが、実際には使わず ruff に検出された。ヘルパー関数内のローカルインポートは lint で見つかりやすいが書き忘れやすい

### 次回への学び

- サブクラス例外を使う場合、既存の `except ParentError` ブロックをすべてチェックして「意図せず子クラスも捕捉していないか」を確認する。特にループ内のスキップロジックは要注意
- `finally` ブロックで elapsed ログを書く設計は、タイムアウト・例外時にも終了ログが出て運用でトラブルシュートしやすい。CLI ラッパーの標準パターンとして採用する価値がある
- `subprocess.run` のタイムアウト処理は Python 3.9+ では自動 kill されるため手動 kill 不要。ドキュメントで確認して実装コストを削減できた

### 残タスク・技術的負債

- `test_main_exits_1_on_missing_env` が monkeypatch のモジュールキャッシュ問題で既存失敗のまま（本 PR スコープ外）
- `AUTH_FAILED` の文字列は Plaud CLI の出力仕様依存。CLI バージョンアップ時に回帰テストが壊れるリスクがある。将来的には実際の CLI 出力サンプルをフィクスチャとして管理する
