# 設計仕様: plaud-importer

**最終更新**: 2026-06-14  
**ステータス**: 草案  
**対応要件**: [docs/requirements/plaud-importer.md](../requirements/plaud-importer.md)

---

## モジュール構成

```
life_analytics/
├── __init__.py
├── plaud_importer.py      # CLI エントリーポイント・オーケストレーション
├── plaud_client.py        # Plaud CLI のサブプロセスラッパー
├── obsidian_writer.py     # Obsidian ファイル書き込み
└── config.py              # 環境変数読み込み

tests/
├── test_plaud_client.py
├── test_obsidian_writer.py
└── test_plaud_importer.py

pyproject.toml
.env.example
```

---

## 設定 (config.py)

```python
@dataclass(frozen=True)
class Config:
    vault_path: Path        # OBSIDIAN_VAULT_PATH (必須)
    plaud_cli: str          # PLAUD_CLI (デフォルト: "npx @plaud-ai/cli")
    log_level: str          # LOG_LEVEL (デフォルト: "INFO")
```

- `python-dotenv` でプロジェクトルートの `.env` を自動ロード
- `OBSIDIAN_VAULT_PATH` が未設定なら `ValueError` を raise して終了

---

## Plaud CLI クライアント (plaud_client.py)

### データモデル

```python
@dataclass
class PlaudRecording:
    id: str
    name: str
    start_at: datetime      # 録音開始時刻（ローカルタイム）
    created_at: datetime    # アップロード時刻
    duration_ms: int        # 録音長（ミリ秒）
```

### 主要メソッド

```python
class PlaudClient:
    def fetch_recordings(self, target_date: date) -> list[PlaudRecording]:
        """対象日の録音一覧を取得する。"""

    def fetch_summary(self, file_id: str) -> str:
        """録音の AI 要約を取得する。取得失敗時は空文字列を返す。"""
```

### 実装方針

**録音取得フロー:**
1. `target_date` から現在日時までの経過日数を算出し `days = elapsed + 2` とする
2. `{cli} recent --days {days}` を subprocess で実行（stdout を JSON としてパース）
3. `start_at.date() == target_date` のものだけをフィルタリングして返す

**要注意点:**
- Plaud CLI の出力フォーマット（JSON 構造）は実装時に `npx @plaud-ai/cli recent --days 2` を実際に実行して確認する
- `start_at` フィールドがタイムゾーン付きの場合はローカルタイムに変換してから比較する
- `summary` コマンドの出力はプレーンテキストと想定する

**エラーハンドリング:**

| 状況 | 対処 |
|---|---|
| CLI コマンドが見つからない (FileNotFoundError) | `PlaudCLIError` を raise |
| 終了コード != 0 | stderr を含む `PlaudCLIError` を raise |
| JSON パース失敗 | `PlaudCLIError` を raise |
| `summary` 取得失敗 | WARNING ログ → 空文字列を返す（処理続行） |

---

## Obsidian ライター (obsidian_writer.py)

### 主要メソッド

```python
class ObsidianWriter:
    def __init__(self, vault_path: Path) -> None: ...

    def process_recording(
        self,
        recording: PlaudRecording,
        summary: str,
        target_date: date,
    ) -> Literal["created", "skipped"]:
        """ルーティングを判定し、適切なメソッドに委譲する。"""

    def append_idea_to_daily_note(
        self,
        recording: PlaudRecording,
        summary: str,
        target_date: date,
    ) -> None:
        """IDEA_ 録音を Daily Note の Plaud セクションに追記する。"""

    def create_standalone_note(
        self,
        recording: PlaudRecording,
        summary: str,
        target_date: date,
    ) -> Path:
        """単独ノートを作成し、ファイルパスを返す。既存なら PlaudNoteExistsError を raise する。"""

    def append_link_to_daily_note(
        self,
        recording: PlaudRecording,
        note_path: Path,
        target_date: date,
    ) -> None:
        """Daily Note の Plaud セクションに WikiLink を追記する。"""
```

### ルーティング判定

```python
IDEA_PREFIX = "IDEA_"

def _route(name: str) -> Literal["idea", "standalone"]:
    return "idea" if name.startswith(IDEA_PREFIX) else "standalone"
```

### Daily Note パス

```python
def _daily_note_path(self, d: date) -> Path:
    return self.vault_path / "Daily" / f"{d.year:04d}" / f"{d.month:02d}" / f"{d.year:04d}-{d.month:02d}-{d.day:02d}.md"
```

Daily Note が存在しない場合は空ファイルを新規作成する。

### Plaud セクションの追記ルール

- `## Plaud` 見出しがなければファイル末尾に `\n\n## Plaud\n` を追加する
- エントリの重複チェック: `recording.id` を含む行が既に存在すれば追記しない

### IDEA_ エントリ形式（Daily Note への直接追記）

```markdown
### 💡 {name}
<!-- plaud:{id} -->
- **時刻**: {HH:MM}
- **長さ**: {duration}

> {summary_line_1}
> {summary_line_2}
```

- `summary` が空の場合は `> （要約なし）` とする
- 複数行の要約は各行先頭に `> ` を付与する

### 単独ノートのリンク形式（Daily Note への追記）

```markdown
- [[Notes/PLAUD/{filename}|{display_name}]] — {duration}
  <!-- plaud:{id} -->
```

- `display_name` はプレフィックスを含んだ元のタイトル（`MEETING_Weekly_Sync` 等）

### 単独ノート形式（Notes/PLAUD/{filename}.md）

```markdown
---
plaud_id: {id}
date: {YYYY-MM-DD}
duration: {duration}
source: plaud
---

# {name}

**日時**: {YYYY-MM-DD HH:MM}  
**長さ**: {duration}

## 要約

{summary}
```

### ファイル名生成

```python
def _note_filename(self, recording: PlaudRecording, d: date) -> str:
    sanitized = re.sub(r'[\\/:*?"<>|]', "_", recording.name)
    return f"{d.isoformat()}-{sanitized}.md"
```

### 冪等性の保証

| ケース | 判定方法 | 対処 |
|---|---|---|
| 単独ノート重複 | ファイルパスが既存 | スキップ（WARNING ログ） |
| IDEA_ エントリ重複 | Daily Note 内に `<!-- plaud:{id} -->` が存在 | スキップ（WARNING ログ） |
| リンク重複 | Daily Note 内に `<!-- plaud:{id} -->` が存在 | スキップ（WARNING ログ） |

---

## CLI エントリーポイント (plaud_importer.py)

```python
def main() -> None:
    args = parse_args()          # --date YYYY-MM-DD
    config = load_config()
    setup_logging(config.log_level)

    target_date = args.date or date.today() - timedelta(days=1)

    client = PlaudClient(config.plaud_cli)
    writer = ObsidianWriter(config.vault_path)

    recordings = client.fetch_recordings(target_date)
    logger.info(f"{len(recordings)} recording(s) found for {target_date}")

    results = {"created": 0, "skipped": 0, "failed": 0}
    for rec in recordings:
        summary = client.fetch_summary(rec.id)
        try:
            status = writer.process_recording(rec, summary, target_date)
            results[status] += 1
        except Exception as e:
            logger.error(f"Failed to process {rec.name}: {e}")
            results["failed"] += 1

    logger.info(f"Done: {results}")
    if results["failed"] > 0:
        sys.exit(1)
```

---

## ユーティリティ

### duration フォーマット

```python
def format_duration(ms: int) -> str:
    s = ms // 1000
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h > 0:
        return f"{h}h{m:02d}m{sec:02d}s"
    elif m > 0:
        return f"{m}m{sec:02d}s"
    return f"{sec}s"
```

---

## 依存関係

### pyproject.toml（想定）

```toml
[project]
name = "life-analytics-platform"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.4",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

依存は最小限。subprocess / pathlib / json / argparse / datetime はすべて標準ライブラリ。

---

## .env.example への追加項目

```bash
# Obsidian Vault の絶対パス（必須）
OBSIDIAN_VAULT_PATH=/Users/yourname/SecondBrain

# Plaud CLI コマンド（任意）
# PLAUD_CLI=npx @plaud-ai/cli

# ログレベル（任意）
# LOG_LEVEL=INFO
```

---

## テスト方針

| テストファイル | 対象 | モック |
|---|---|---|
| `test_plaud_client.py` | CLI コマンド呼び出し・JSON パース・日付フィルタ | `subprocess.run` |
| `test_obsidian_writer.py` | ファイル生成・追記・冪等性 | `tmp_path` (pytest fixture) |
| `test_plaud_importer.py` | 引数パース・オーケストレーション | PlaudClient, ObsidianWriter をモック |

実際の Plaud API は叩かない。`tests/integration/` に実環境テストを分離する（CI では実行しない）。
