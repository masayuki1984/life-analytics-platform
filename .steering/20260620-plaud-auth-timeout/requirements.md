# 要件定義: plaud-importer 認証エラー・タイムアウト対応

**作成日**: 2026-06-20

---

## 概要

Mac mini の self-hosted runner（gha-runner）で plaud-importer を実行した際、
Plaud CLI の認証トークンが期限切れになり `AUTH_FAILED` エラーで処理が長時間停止する問題が発生した。
CLIサブプロセスにタイムアウトを設定し、認証エラーを即座に検知して早期終了・明示的なエラーメッセージを出力することで、
夜間の自動実行で無限ハングを防ぐ。

## スコープ

### IN（実装する）

- `PlaudClient._run()` にタイムアウトを設定する（デフォルト 60 秒、環境変数 `PLAUD_TIMEOUT` で変更可能）
- `_run()` 実行前後にコマンド・開始時刻・終了時刻・実行時間をログ出力する
- `AUTH_FAILED` を stdout/stderr から検知し `PlaudAuthenticationError` を raise する
- `PlaudAuthenticationError` 発生時は即時終了し「plaud login を実行してください」を表示する
- subprocess の戻り値チェックを強化する（returncode != 0 に加えて AUTH_FAILED 文字列を優先チェック）
- `dry-run` モードでも同じエラーハンドリングを適用する（`fetch_summary` が AUTH_FAILED を握りつぶさない）
- `PLAUD_TIMEOUT` を `Config` に追加し `.env.example` にも記載する
- テストを追加する（AUTH_FAILED・timeout・正常系）
- README にログイン方法とトークン切れ時の復旧手順を追記する

### OUT（実装しない）

- 自動再ログイン・ブラウザ起動
- リトライロジック（認証切れはリトライしても解決しないため）
- Plaud CLI 以外の認証方式への対応

## 機能要件

### 主要機能

1. **タイムアウト制御**: `subprocess.run(..., timeout=self._timeout)` で上限を設ける。`TimeoutExpired` は `PlaudCLIError` に変換する
2. **認証エラー検知**: `AUTH_FAILED` が stdout または stderr に含まれる場合、`returncode` チェックより先に `PlaudAuthenticationError` を raise する
3. **実行ログ**: `_run()` 内で DEBUG レベルにてコマンド・開始・終了・経過秒数を記録する
4. **エラー伝播**: `fetch_summary()` は `PlaudAuthenticationError` を握りつぶさずに上位へ伝播させる
5. **即時終了**: `main()` が `PlaudAuthenticationError` を捕捉したら exit code 1 で終了し、復旧手順を ERROR ログに出力する

### データ要件

- **入力**: 環境変数 `PLAUD_TIMEOUT`（秒数、整数、デフォルト 60）
- **出力**: エラーログ（stderr）
- **保存先**: なし

## 非機能要件

- **パフォーマンス**: タイムアウト発生時はプロセスを kill してから例外を raise する（ゾンビプロセス防止）
- **エラーハンドリング**: `PlaudAuthenticationError` は `PlaudCLIError` のサブクラス。既存の `except PlaudCLIError` は引き続き動作する
- **ログ**: CLI 実行ログは DEBUG レベル。AUTH_FAILED・timeout の検知は ERROR レベル

## 受け入れ条件

- [ ] `PLAUD_TIMEOUT=5` 設定時、5 秒以上かかるコマンドが `PlaudCLIError` (timeout) で終了する
- [ ] `AUTH_FAILED` を含む CLI 出力が `PlaudAuthenticationError` を raise する
- [ ] `PlaudAuthenticationError` 発生時、`main()` が exit 1 し「plaud login を実行してください」を出力する
- [ ] `--dry-run` 時も AUTH_FAILED は即時終了する
- [ ] `pytest` が全 GREEN
- [ ] `ruff check .` が通る
- [ ] README にログイン手順・復旧手順が記載されている
