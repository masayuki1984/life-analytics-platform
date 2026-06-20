# 技術設計: plaud-importer 認証エラー・タイムアウト対応

**作成日**: 2026-06-20

---

## アーキテクチャ概要

変更は `config.py` と `plaud_client.py` と `plaud_importer.py` の 3 ファイルに集中する。
`obsidian_writer.py` は変更なし。

```
環境変数(PLAUD_TIMEOUT)
        ↓
   config.py (Config.plaud_timeout)
        ↓
PlaudClient.__init__(timeout=config.plaud_timeout)
        ↓
PlaudClient._run()
  ├─ DEBUG: コマンド・開始時刻をログ
  ├─ subprocess.run(..., timeout=self._timeout)
  │    ├─ TimeoutExpired → PlaudCLIError("タイムアウト")
  │    └─ FileNotFoundError → PlaudCLIError("CLI が見つからない")
  ├─ stdout/stderr に "AUTH_FAILED" → PlaudAuthenticationError
  ├─ returncode != 0 → PlaudCLIError
  └─ DEBUG: 終了時刻・経過秒数をログ
        ↓
fetch_recordings()       fetch_summary()
  PlaudAuthenticationError は握りつぶさず伝播
        ↓
plaud_importer.main()
  except PlaudAuthenticationError → ERROR ログ + exit(1)
  except PlaudCLIError            → ERROR ログ + exit(1)
```

## ディレクトリ・ファイル構成

変更ファイルのみ記載（新規ファイルなし）。

```
life_analytics/
├── config.py          # plaud_timeout フィールド追加
├── plaud_client.py    # PlaudAuthenticationError / タイムアウト / 実行ログ
└── plaud_importer.py  # PlaudAuthenticationError ハンドリング・timeout 引き渡し

tests/
└── test_plaud_client.py  # AUTH_FAILED / timeout / 正常系テスト追加

.env.example           # PLAUD_TIMEOUT 追記
README.md              # ログイン手順・復旧手順追記
```

## 主要クラス・関数設計

### `PlaudAuthenticationError`

```python
class PlaudAuthenticationError(PlaudCLIError):
    """Plaud CLI の認証トークンが無効または期限切れ。"""
    pass
```

`PlaudCLIError` のサブクラスにすることで、既存の `except PlaudCLIError` ブロックが
引き続き機能する（後方互換）。`main()` では先に `PlaudAuthenticationError` を捕捉して
専用メッセージを出す。

### `PlaudClient.__init__`

```python
class PlaudClient:
    def __init__(self, cli: str, timeout: int = 60) -> None:
        self._cli = cli
        self._timeout = timeout
```

### `PlaudClient._run`（変更後）

```python
_AUTH_FAILED_RE = re.compile(r"AUTH_FAILED")

def _run(self, *args: str) -> str:
    cmd = self._cli.split() + list(args)
    t0 = datetime.now()
    logger.debug("Plaud CLI 開始: %s  [%s]", " ".join(cmd), t0.strftime("%H:%M:%S"))

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False,
            timeout=self._timeout,
        )
    except FileNotFoundError as e:
        raise PlaudCLIError(f"Plaud CLI が見つかりません: {self._cli}") from e
    except subprocess.TimeoutExpired as e:
        raise PlaudCLIError(
            f"Plaud CLI がタイムアウトしました ({self._timeout}s): {' '.join(cmd)}"
        ) from e
    finally:
        elapsed = (datetime.now() - t0).total_seconds()
        logger.debug("Plaud CLI 終了: %s  経過 %.1fs", " ".join(cmd), elapsed)

    # AUTH_FAILED は returncode チェックより先に判定する
    combined = result.stdout + result.stderr
    if _AUTH_FAILED_RE.search(combined):
        raise PlaudAuthenticationError(
            "Plaud CLI の認証が期限切れです。`plaud login` を実行してください。"
        )

    if result.returncode != 0:
        raise PlaudCLIError(
            f"Plaud CLI がエラーで終了しました (exit {result.returncode}): "
            f"{result.stderr.strip()}"
        )

    return result.stdout
```

**注意**: `finally` ブロックで elapsed をログする設計にすることで、
タイムアウト・例外時も終了ログが必ず出る。

### `PlaudClient.fetch_summary`（変更後）

```python
def fetch_summary(self, file_id: str) -> str:
    try:
        output = self._run("summary", file_id)
        return _parse_summary(output)
    except PlaudAuthenticationError:
        raise  # 認証エラーは握りつぶさない
    except Exception as e:
        logger.warning(f"要約の取得に失敗しました [{file_id}]: {e}")
        return ""
```

### `Config`（変更後）

```python
@dataclass(frozen=True)
class Config:
    vault_path: Path
    plaud_cli: str
    plaud_timeout: int   # 追加
    log_level: str
```

`load_config()` で `PLAUD_TIMEOUT` を読み取る。不正値（非整数・0以下）は `ValueError`。

### `main()`（変更後）

```python
from life_analytics.plaud_client import PlaudAuthenticationError, PlaudClient, PlaudCLIError

# PlaudClient 生成時に timeout を渡す
client = PlaudClient(config.plaud_cli, timeout=config.plaud_timeout)

# fetch_recordings の例外ハンドリング
try:
    recordings = client.fetch_recordings(target_date)
except PlaudAuthenticationError as e:
    logger.error(str(e))
    logger.error("復旧手順: `plaud login` を実行して再認証してください。")
    sys.exit(1)
except PlaudCLIError as e:
    logger.error(f"録音の取得に失敗しました: {e}")
    sys.exit(1)

# fetch_summary の例外ハンドリング（ループ内）
for rec in recordings:
    try:
        summary = client.fetch_summary(rec.id)
    except PlaudAuthenticationError as e:
        logger.error(str(e))
        logger.error("復旧手順: `plaud login` を実行して再認証してください。")
        sys.exit(1)
    try:
        status = writer.process_recording(rec, summary, target_date)
        ...
```

## データスキーマ

### 入力（環境変数）

| 変数名 | 型 | デフォルト | 説明 |
|---|---|---|---|
| `PLAUD_TIMEOUT` | int (秒) | `60` | CLI 1 回あたりのタイムアウト |

### 出力

- エラーログ（stderr）: `AUTH_FAILED` 時・タイムアウト時に ERROR レベルで出力
- DEBUG ログ（stderr）: 各 CLI 呼び出しのコマンド・開始・終了・経過時間

## 依存関係

- 既存モジュール: `life_analytics/plaud_client.py`, `life_analytics/config.py`, `life_analytics/plaud_importer.py`
- 外部ライブラリ: 追加なし（`subprocess`, `datetime`, `re` はすべて標準ライブラリ）

## 技術的判断・トレードオフ

| 判断 | 採用案 | 却下案 | 理由 |
|---|---|---|---|
| `PlaudAuthenticationError` の継承元 | `PlaudCLIError` のサブクラス | 独立した例外 | 既存の `except PlaudCLIError` ブロックを壊さない後方互換性 |
| AUTH_FAILED の検出場所 | `_run()` 内（returncode チェック前） | 各メソッドで個別検出 | 検出ロジックを 1 箇所に集約、漏れを防ぐ |
| 実行ログのレベル | DEBUG | INFO | 録音件数が多い場合に毎コマンドINFOが出ると過剰になるため |
| タイムアウト後のプロセス | `subprocess.run` に任せる（自動 kill） | 手動 kill | Python 3.9+ の `subprocess.run` は `TimeoutExpired` 発生時に自動で kill する |

## 懸念事項・リスク

- `npx @plaud-ai/cli` は Node.js の起動時間が数秒かかる。デフォルト 60 秒は十分な余裕があるが、ネットワークが遅い環境では要調整
- `AUTH_FAILED` の文字列は Plaud CLI の出力仕様に依存する。CLI のバージョンアップで変わる可能性がある
