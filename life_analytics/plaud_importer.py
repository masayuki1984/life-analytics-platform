from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, timedelta

from life_analytics.config import load_config
from life_analytics.obsidian_writer import ObsidianWriter
from life_analytics.plaud_client import PlaudClient, PlaudCLIError

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plaud 録音を Obsidian へインポートする",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "例:\n"
            "  python -m life_analytics.plaud_importer\n"
            "  python -m life_analytics.plaud_importer --date 2026-06-14\n"
            "  python -m life_analytics.plaud_importer --dry-run\n"
        ),
    )
    parser.add_argument(
        "--date",
        type=date.fromisoformat,
        default=None,
        metavar="YYYY-MM-DD",
        help="処理対象日（省略時は昨日）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="ファイルを書き込まずに処理内容を表示する",
    )
    return parser.parse_args()


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )


def main() -> None:
    args = parse_args()

    try:
        config = load_config()
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    setup_logging(config.log_level)

    target_date: date = args.date or date.today() - timedelta(days=1)

    if args.dry_run:
        logger.info("--- DRY-RUN モード（ファイルは書き込まれません）---")

    logger.info(f"処理対象日: {target_date}  Vault: {config.vault_path}")

    client = PlaudClient(config.plaud_cli)
    writer = ObsidianWriter(config.vault_path, dry_run=args.dry_run)

    try:
        recordings = client.fetch_recordings(target_date)
    except PlaudCLIError as e:
        logger.error(f"録音の取得に失敗しました: {e}")
        sys.exit(1)

    logger.info(f"{len(recordings)} 件の録音が見つかりました")

    results: dict[str, int] = {"created": 0, "skipped": 0, "failed": 0}
    for rec in recordings:
        summary = client.fetch_summary(rec.id)
        try:
            status = writer.process_recording(rec, summary, target_date)
            results[status] += 1
        except Exception as e:
            logger.error(f"処理に失敗しました [{rec.name}]: {e}")
            results["failed"] += 1

    logger.info(
        f"完了: created={results['created']}  skipped={results['skipped']}  "
        f"failed={results['failed']}"
    )

    if results["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
