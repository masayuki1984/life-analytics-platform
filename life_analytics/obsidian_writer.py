from __future__ import annotations

import logging
import re
from datetime import date
from pathlib import Path
from typing import Literal

from life_analytics.plaud_client import PlaudRecording

logger = logging.getLogger(__name__)

IDEA_PREFIX = "IDEA_"

# ファイル名に使えない文字（Windows 互換 + 空白）
_FILENAME_UNSAFE = re.compile(r'[\\/:*?"<>|\s]')


class ObsidianWriter:
    def __init__(self, vault_path: Path, dry_run: bool = False) -> None:
        self.vault_path = vault_path
        self.dry_run = dry_run

    def process_recording(
        self,
        recording: PlaudRecording,
        summary: str,
        target_date: date,
    ) -> Literal["created", "skipped"]:
        """ルーティングを判定して処理を委譲する。"""
        if recording.name.startswith(IDEA_PREFIX):
            return self._process_idea(recording, summary, target_date)
        return self._process_standalone(recording, summary, target_date)

    # ------------------------------------------------------------------
    # IDEA_ 処理
    # ------------------------------------------------------------------

    def _process_idea(
        self,
        recording: PlaudRecording,
        summary: str,
        target_date: date,
    ) -> Literal["created", "skipped"]:
        daily_path = self._ensure_daily_note(target_date)

        if self._is_already_imported(daily_path, recording.id):
            logger.warning(f"[skip] インポート済み: {recording.name}")
            return "skipped"

        self._ensure_plaud_section(daily_path)
        entry = _format_idea_entry(recording, summary)

        if self.dry_run:
            logger.info(f"[DRY-RUN] Daily Note に IDEA を追記します: {recording.name}\n{entry}")
        else:
            with open(daily_path, "a", encoding="utf-8") as f:
                f.write("\n" + entry + "\n")
            logger.info(f"[created] IDEA を追記しました ({daily_path.name}): {recording.name}")

        return "created"

    # ------------------------------------------------------------------
    # 単独ノート処理（MEETING_ / SEMINAR_ / STUDY_ / prefixなし）
    # ------------------------------------------------------------------

    def _process_standalone(
        self,
        recording: PlaudRecording,
        summary: str,
        target_date: date,
    ) -> Literal["created", "skipped"]:
        notes_dir = self.vault_path / "Notes" / "PLAUD"
        notes_dir.mkdir(parents=True, exist_ok=True)

        filename = _note_filename(recording, target_date)
        note_path = notes_dir / filename

        if note_path.exists():
            logger.warning(f"[skip] ノートが既に存在します: {note_path.name}")
            # ノートは存在するが Daily Note のリンクが未追記の場合に備えて冪等追記
            self._append_link_if_missing(recording, note_path, target_date)
            return "skipped"

        content = _format_standalone_note(recording, summary, target_date)

        if self.dry_run:
            logger.info(f"[DRY-RUN] ノートを作成します: {note_path}\n{content}")
        else:
            note_path.write_text(content, encoding="utf-8")
            logger.info(f"[created] ノートを作成しました: {note_path.name}")

        self._append_link_if_missing(recording, note_path, target_date)
        return "created"

    def _append_link_if_missing(
        self,
        recording: PlaudRecording,
        note_path: Path,
        target_date: date,
    ) -> None:
        daily_path = self._ensure_daily_note(target_date)

        if self._is_already_imported(daily_path, recording.id):
            return

        self._ensure_plaud_section(daily_path)

        rel = note_path.relative_to(self.vault_path)
        # Obsidian WikiLink はスラッシュ区切り・拡張子なし
        link_str = str(rel.with_suffix("")).replace("\\", "/")
        link_entry = (
            f"- [[{link_str}|{recording.name}]] — {recording.duration}\n"
            f"  <!-- plaud:{recording.id} -->"
        )

        if self.dry_run:
            logger.info(
                f"[DRY-RUN] Daily Note にリンクを追記します: {recording.name}\n{link_entry}"
            )
        else:
            with open(daily_path, "a", encoding="utf-8") as f:
                f.write("\n" + link_entry + "\n")
            logger.info(f"[created] リンクを追記しました ({daily_path.name}): {recording.name}")

    # ------------------------------------------------------------------
    # Daily Note ユーティリティ
    # ------------------------------------------------------------------

    def _ensure_daily_note(self, d: date) -> Path:
        path = self._daily_note_path(d)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            if self.dry_run:
                logger.info(f"[DRY-RUN] Daily Note を作成します: {path}")
            else:
                path.touch()
                logger.info(f"[created] Daily Note を作成しました: {path.name}")
        return path

    def _daily_note_path(self, d: date) -> Path:
        return (
            self.vault_path
            / "Daily"
            / f"{d.year:04d}"
            / f"{d.month:02d}"
            / f"{d.year:04d}-{d.month:02d}-{d.day:02d}.md"
        )

    def _ensure_plaud_section(self, note_path: Path) -> None:
        """dry_run 時は何もしない（実ファイルを読まない）。"""
        if self.dry_run:
            return
        text = note_path.read_text(encoding="utf-8")
        if "## Plaud" not in text:
            with open(note_path, "a", encoding="utf-8") as f:
                f.write("\n\n## Plaud\n")

    def _is_already_imported(self, note_path: Path, recording_id: str) -> bool:
        """<!-- plaud:{id} --> マーカーの存在で重複チェックする。"""
        if self.dry_run or not note_path.exists():
            return False
        return f"plaud:{recording_id}" in note_path.read_text(encoding="utf-8")


# ------------------------------------------------------------------
# フォーマット関数（純粋関数）
# ------------------------------------------------------------------


def _note_filename(recording: PlaudRecording, d: date) -> str:
    sanitized = _FILENAME_UNSAFE.sub("_", recording.name)
    return f"{d.isoformat()}-{sanitized}.md"


def _format_idea_entry(recording: PlaudRecording, summary: str) -> str:
    time_str = recording.start_at.strftime("%H:%M")
    marker = f"<!-- plaud:{recording.id} -->"
    quoted = _quote_summary(summary)
    return (
        f"### 💡 {recording.name}\n"
        f"{marker}\n"
        f"- **時刻**: {time_str}\n"
        f"- **長さ**: {recording.duration}\n"
        f"\n"
        f"{quoted}"
    )


def _format_standalone_note(
    recording: PlaudRecording,
    summary: str,
    d: date,
) -> str:
    dt_str = recording.start_at.strftime("%Y-%m-%d %H:%M")
    summary_body = summary if summary else "（要約なし）"
    return (
        f"---\n"
        f"plaud_id: {recording.id}\n"
        f"date: {d.isoformat()}\n"
        f"duration: {recording.duration}\n"
        f"source: plaud\n"
        f"---\n"
        f"\n"
        f"# {recording.name}\n"
        f"\n"
        f"**日時**: {dt_str}  \n"
        f"**長さ**: {recording.duration}\n"
        f"\n"
        f"## 要約\n"
        f"\n"
        f"{summary_body}\n"
    )


def _quote_summary(summary: str) -> str:
    if not summary:
        return "> （要約なし）"
    return "\n".join(f"> {line}" if line.strip() else ">" for line in summary.splitlines())
