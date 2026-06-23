# 技術設計: obsidian-daily-note-commands

**作成日**: 2026-06-23

---

## アーキテクチャ概要

```
CLI 引数 (argparse)
    │
    ▼
load_dotenv() → OBSIDIAN_VAULT_ROOT
    │
    ├─[create_daily_note]──────────────────────────────────────────
    │   get_daily_note_path(vault_root, date) → Path
    │   get_template_content(vault_root) → str   ← エラー時 sys.exit(1)
    │   create_daily_note(vault_root, date) → "created" | "skipped"
    │       ├── 存在チェック → skipped (exit 0)
    │       ├── mkdir -p
    │       └── template をコピーして書き込み → created (exit 0)
    │
    └─[append_plaud_link]─────────────────────────────────────────
        get_daily_note_path(vault_root, date) → Path
        Daily Note 存在チェック → なければ skip (exit 0)
        Daily Note に "## Plaud" 存在チェック → なければ skip (exit 0)
        collect_plaud_notes(vault_root, date) → list[PlaudNoteInfo]
        各ノートについて重複チェック → 未追記のみ挿入
        append_to_plaud_section(content, entry) → str
        ファイルに書き戻し → exit 0
```

## ディレクトリ・ファイル構成

```
life_analytics/
└── obsidian/
    ├── __init__.py
    ├── create_daily_note.py    # Daily Note 作成コマンド
    └── append_plaud_link.py    # Plaud リンク追記コマンド

tests/
├── test_create_daily_note.py
└── test_append_plaud_link.py
```

## 主要関数設計

### `create_daily_note.py`

```python
TZ = ZoneInfo("Asia/Tokyo")

def load_vault_root() -> Path:
    """OBSIDIAN_VAULT_ROOT を env から読み込む。未設定なら ValueError。"""

def get_daily_note_path(vault_root: Path, d: date) -> Path:
    """Daily/YYYY/MM/YYYY-MM-DD.md の絶対パスを返す。"""

def get_template_content(vault_root: Path) -> str:
    """Templates/daily.md を読む。存在しなければ FileNotFoundError。"""

def create_daily_note(vault_root: Path, d: date) -> Literal["created", "skipped"]:
    """Daily Note を作成する（冪等）。"""

def main() -> None:
    """argparse で --date を受け取り create_daily_note を呼ぶ。"""
```

### `append_plaud_link.py`

```python
@dataclass
class PlaudNoteInfo:
    path: Path
    plaud_id: str
    name: str       # # 見出しから抽出した元の録音名
    duration: str

def load_vault_root() -> Path: ...

def get_daily_note_path(vault_root: Path, d: date) -> Path: ...

def parse_plaud_note(path: Path, vault_root: Path) -> PlaudNoteInfo | None:
    """frontmatter と # 見出しをパースして PlaudNoteInfo を返す。"""

def collect_plaud_notes(vault_root: Path, d: date) -> list[PlaudNoteInfo]:
    """Notes/PLAUD/{date}-*.md を収集してパースする。"""

def format_link_entry(info: PlaudNoteInfo, vault_root: Path) -> str:
    """- [[path|name]] — duration\n  <!-- plaud:id --> を返す。"""

def append_to_plaud_section(content: str, entry: str) -> str:
    """## Plaud セクションの末尾（次の ## の前）にエントリを挿入した文字列を返す。"""

def append_plaud_link(vault_root: Path, d: date) -> str:
    """Daily Note に Plaud リンクを追記する。戻り値はログ用ステータス文字列。"""

def main() -> None: ...
```

## データスキーマ

### Plaud ノートファイル（frontmatter）

```
---
plaud_id: {id}
date: YYYY-MM-DD
duration: {duration}
source: plaud
---

# {recording_name}
```

### Daily Note リンクエントリ形式

```
- [[Notes/PLAUD/2026-06-22-MEETING_foo|MEETING_foo]] — 42m05s
  <!-- plaud:aabbccddeeff00112233445566778899 -->
```

### 重複チェック

Daily Note 内に `<!-- plaud:{id} -->` が存在すれば追記済みとみなす。

## 依存関係

- 既存モジュール: なし（独立実装）
- 外部ライブラリ: `python-dotenv`（既存依存）、`zoneinfo`（stdlib Python 3.9+）

## 技術的判断・トレードオフ

| 判断 | 理由 |
|---|---|
| `OBSIDIAN_VAULT_ROOT` を `OBSIDIAN_VAULT_PATH` と別名にする | 既存 `config.py` を壊さず独立したスコープで追加できる |
| `ObsidianWriter` を再利用しない | テンプレート未存在時の挙動が異なる（WARNING vs エラー終了）。独立実装の方がシンプル |
| `append_to_plaud_section` で末尾追記でなく section 内挿入 | テンプレートの `## メモ` 等の後続セクションを壊さない |
| 重複チェックに `<!-- plaud:{id} -->` を使う | 既存 `obsidian_writer.py` との互換性。同じマーカーで二重インポートを防止 |

## 懸念事項・リスク

- `Notes/PLAUD/` が存在しない場合は空リストを返し正常終了（ログなし）
- Daily Note に `## Plaud` が複数ある場合、最初の `## Plaud` だけを対象にする
