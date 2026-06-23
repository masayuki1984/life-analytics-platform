"""Daily Note 作成コマンド。

python -m life_analytics.obsidian.create_daily_note
python -m life_analytics.obsidian.create_daily_note --date 2026-06-23
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

TZ = ZoneInfo("Asia/Tokyo")


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


def get_template_content(vault_root: Path) -> str:
    """Templates/daily.md を読む。存在しなければ FileNotFoundError。"""
    template_path = vault_root / "Templates" / "daily.md"
    if not template_path.exists():
        raise FileNotFoundError(f"テンプレートファイルが存在しません: {template_path}")
    return template_path.read_text(encoding="utf-8")


def create_daily_note(vault_root: Path, d: date) -> Literal["created", "skipped"]:
    """Daily Note を作成する（冪等）。既存ファイルは上書きしない。"""
    note_path = get_daily_note_path(vault_root, d)

    if note_path.exists():
        logger.info(f"[skip] 既に存在するためスキップ: {note_path}")
        return "skipped"

    content = get_template_content(vault_root)

    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(content, encoding="utf-8")
    logger.info(f"[created] Daily Note を作成しました: {note_path}")
    return "created"


def main() -> None:
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="Obsidian Daily Note を作成する")
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help="対象日付（省略時は Asia/Tokyo の今日）",
    )
    args = parser.parse_args()

    if args.date:
        try:
            target_date = date.fromisoformat(args.date)
        except ValueError:
            logger.error(f"--date の形式が不正です（YYYY-MM-DD で指定してください）: {args.date}")
            sys.exit(1)
    else:
        target_date = datetime.now(tz=TZ).date()

    try:
        vault_root = load_vault_root()
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    try:
        create_daily_note(vault_root, target_date)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
