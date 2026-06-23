"""Plaud リンク追記コマンド。

Daily Note の ## Plaud セクションに Plaud 録音ノートのリンクを追記する。

python -m life_analytics.obsidian.append_plaud_link
python -m life_analytics.obsidian.append_plaud_link --date 2026-06-22
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

TZ = ZoneInfo("Asia/Tokyo")

_FM_PATTERN = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
_HEADING_PATTERN = re.compile(r"^# (.+)$", re.MULTILINE)


@dataclass(frozen=True)
class PlaudNoteInfo:
    path: Path
    plaud_id: str
    name: str
    duration: str


def load_vault_root() -> Path:
    """OBSIDIAN_VAULT_ROOT を環境変数から読み込む。未設定なら ValueError。"""
    val = os.environ.get("OBSIDIAN_VAULT_ROOT")
    if not val:
        raise ValueError(
            "OBSIDIAN_VAULT_ROOT が未設定です。.env または環境変数に設定してください。"
        )
    return Path(val).expanduser().resolve()


def get_daily_note_path(vault_root: Path, d: date) -> Path:
    """Daily/YYYY/MM/YYYY-MM-DD.md の絶対パスを返す。"""
    return vault_root / "Daily" / f"{d.year:04d}" / f"{d.month:02d}" / f"{d.isoformat()}.md"


def _parse_frontmatter(content: str) -> dict[str, str]:
    """YAML frontmatter をパースして辞書を返す。"""
    m = _FM_PATTERN.match(content)
    if not m:
        return {}
    result: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ": " in line:
            k, v = line.split(": ", 1)
            result[k.strip()] = v.strip()
    return result


def _extract_heading(content: str) -> str | None:
    """# 見出しから録音名を抽出する。"""
    m = _HEADING_PATTERN.search(content)
    return m.group(1).strip() if m else None


def parse_plaud_note(path: Path, vault_root: Path) -> PlaudNoteInfo | None:
    """Notes/PLAUD/ のファイルをパースして PlaudNoteInfo を返す。パース失敗時は None。"""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None

    fm = _parse_frontmatter(content)
    plaud_id = fm.get("plaud_id")
    duration = fm.get("duration", "")
    name = _extract_heading(content)

    if not plaud_id or not name:
        return None

    return PlaudNoteInfo(path=path, plaud_id=plaud_id, name=name, duration=duration)


def collect_plaud_notes(vault_root: Path, d: date) -> list[PlaudNoteInfo]:
    """指定日の Plaud ノートを収集する。"""
    plaud_dir = vault_root / "Notes" / "PLAUD"
    if not plaud_dir.is_dir():
        return []

    notes = []
    for f in sorted(plaud_dir.glob(f"{d.isoformat()}-*.md")):
        info = parse_plaud_note(f, vault_root)
        if info:
            notes.append(info)
    return notes


def format_link_entry(info: PlaudNoteInfo, vault_root: Path) -> str:
    """Daily Note に追記するリンクエントリを生成する。"""
    rel = info.path.relative_to(vault_root)
    link_str = str(rel.with_suffix("")).replace("\\", "/")
    duration_part = f" — {info.duration}" if info.duration else ""
    return f"- [[{link_str}|{info.name}]]{duration_part}\n  <!-- plaud:{info.plaud_id} -->"


def append_to_plaud_section(content: str, entry: str) -> str:
    """## Plaud セクションの末尾（次の ## の前）にエントリを挿入した文字列を返す。

    ## Plaud セクションが存在しない場合は content をそのまま返す。
    """
    lines = content.splitlines(keepends=True)

    plaud_idx: int | None = None
    for i, line in enumerate(lines):
        if line.rstrip("\n") == "## Plaud":
            plaud_idx = i
            break

    if plaud_idx is None:
        return content

    # 次のセクション（## で始まる行）を探す
    next_section_idx = len(lines)
    for i in range(plaud_idx + 1, len(lines)):
        if lines[i].startswith("## "):
            next_section_idx = i
            break

    # セクション内の末尾の空行をスキップして挿入位置を決める
    insert_idx = next_section_idx
    for i in range(next_section_idx - 1, plaud_idx, -1):
        if lines[i].strip():
            insert_idx = i + 1
            break
    else:
        insert_idx = plaud_idx + 1

    new_entry_lines = [entry + "\n"]
    if insert_idx < len(lines) and lines[insert_idx - 1].strip():
        # 直前に内容があれば空行を入れない（既存コンテンツとの間の改行は保持）
        pass

    new_lines = lines[:insert_idx] + new_entry_lines + lines[insert_idx:]
    return "".join(new_lines)


def append_plaud_link(vault_root: Path, d: date) -> str:
    """Daily Note に Plaud リンクを追記する（冪等）。

    戻り値:
        "appended"           — 1件以上追記した
        "no_new_links"       — 追記対象なし（全て追記済み or Plaudノートなし）
        "skipped_no_note"    — Daily Note が存在しない
        "skipped_no_section" — ## Plaud セクションが存在しない
    """
    note_path = get_daily_note_path(vault_root, d)

    if not note_path.exists():
        logger.info(f"[skip] 対象 Daily Note なしでスキップ: {note_path}")
        return "skipped_no_note"

    content = note_path.read_text(encoding="utf-8")

    if "## Plaud" not in content:
        logger.info(f"[skip] Plaud セクションなしでスキップ: {note_path.name}")
        return "skipped_no_section"

    plaud_notes = collect_plaud_notes(vault_root, d)
    appended = 0

    for info in plaud_notes:
        marker = f"plaud:{info.plaud_id}"
        if marker in content:
            logger.debug(f"[skip] 既にリンク済み: {info.name}")
            continue

        entry = format_link_entry(info, vault_root)
        content = append_to_plaud_section(content, entry)
        logger.info(f"[created] リンクを追記しました ({note_path.name}): {info.name}")
        appended += 1

    if appended > 0:
        note_path.write_text(content, encoding="utf-8")
        return "appended"

    return "no_new_links"


def main() -> None:
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="Daily Note に Plaud リンクを追記する")
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help="対象日付（省略時は Asia/Tokyo の前日）",
    )
    args = parser.parse_args()

    if args.date:
        try:
            target_date = date.fromisoformat(args.date)
        except ValueError:
            logger.error(f"--date の形式が不正です（YYYY-MM-DD で指定してください）: {args.date}")
            sys.exit(1)
    else:
        target_date = (datetime.now(tz=TZ) - timedelta(days=1)).date()

    try:
        vault_root = load_vault_root()
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    append_plaud_link(vault_root, target_date)


if __name__ == "__main__":
    main()
