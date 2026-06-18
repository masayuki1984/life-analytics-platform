from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import pytest

from life_analytics.obsidian_writer import (
    ObsidianWriter,
    _note_filename,
    _quote_summary,
)
from life_analytics.plaud_client import PlaudRecording

# ---------------------------------------------------------------------------
# テスト用フィクスチャ
# ---------------------------------------------------------------------------

TARGET_DATE = date(2026, 6, 14)


def _make_recording(
    name: str = "MEETING_Weekly_Sync",
    file_id: str = "aabbccddeeff00112233445566778899",
    start_at: datetime = datetime(2026, 6, 14, 9, 58, 0),
    duration: str = "42m05s",
) -> PlaudRecording:
    return PlaudRecording(
        id=file_id,
        name=name,
        start_at=start_at,
        created_at=start_at,
        duration=duration,
    )


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    """テスト用の Vault ディレクトリ。"""
    return tmp_path


# ---------------------------------------------------------------------------
# _note_filename
# ---------------------------------------------------------------------------


def test_note_filename_sanitizes_spaces() -> None:
    rec = _make_recording(name="MEETING_Weekly Sync")
    assert _note_filename(rec, TARGET_DATE) == "2026-06-14-MEETING_Weekly_Sync.md"


def test_note_filename_sanitizes_slash() -> None:
    rec = _make_recording(name="STUDY_Python/Django")
    assert "/" not in _note_filename(rec, TARGET_DATE)


# ---------------------------------------------------------------------------
# _quote_summary
# ---------------------------------------------------------------------------


def test_quote_summary_multiline() -> None:
    result = _quote_summary("line1\nline2")
    assert result == "> line1\n> line2"


def test_quote_summary_empty() -> None:
    assert _quote_summary("") == "> （要約なし）"


def test_quote_summary_blank_line_in_middle() -> None:
    result = _quote_summary("line1\n\nline2")
    assert ">\n> line2" in result or ">\n>" in result


# ---------------------------------------------------------------------------
# Daily Note の新規作成
# ---------------------------------------------------------------------------


def test_ensure_daily_note_creates_file(vault: Path) -> None:
    writer = ObsidianWriter(vault)
    rec = _make_recording(name="IDEA_新しいアイデア")
    writer.process_recording(rec, "要約テキスト", TARGET_DATE)

    daily = vault / "Daily" / "2026" / "06" / "2026-06-14.md"
    assert daily.exists()


def test_ensure_daily_note_creates_parent_dirs(vault: Path) -> None:
    writer = ObsidianWriter(vault)
    rec = _make_recording(name="IDEA_テスト")
    writer.process_recording(rec, "", TARGET_DATE)

    assert (vault / "Daily" / "2026" / "06").is_dir()


# ---------------------------------------------------------------------------
# IDEA_ エントリの追記
# ---------------------------------------------------------------------------


def test_idea_appended_to_daily_note(vault: Path) -> None:
    rec = _make_recording(name="IDEA_アイデアタイトル", file_id="a" * 32)
    writer = ObsidianWriter(vault)
    status = writer.process_recording(rec, "要約内容", TARGET_DATE)

    assert status == "created"
    daily = vault / "Daily" / "2026" / "06" / "2026-06-14.md"
    content = daily.read_text(encoding="utf-8")
    assert "## Plaud" in content
    assert "💡 IDEA_アイデアタイトル" in content
    assert f"plaud:{'a' * 32}" in content
    assert "> 要約内容" in content


def test_idea_idempotent(vault: Path) -> None:
    """同じ IDEA_ を 2 回処理してもエントリが重複しない。"""
    rec = _make_recording(name="IDEA_重複テスト", file_id="b" * 32)
    writer = ObsidianWriter(vault)

    status1 = writer.process_recording(rec, "要約", TARGET_DATE)
    status2 = writer.process_recording(rec, "要約", TARGET_DATE)

    assert status1 == "created"
    assert status2 == "skipped"

    daily = vault / "Daily" / "2026" / "06" / "2026-06-14.md"
    content = daily.read_text(encoding="utf-8")
    # マーカーが 1 個だけ存在する
    assert content.count(f"plaud:{'b' * 32}") == 1


# ---------------------------------------------------------------------------
# 単独ノートの作成
# ---------------------------------------------------------------------------


def test_standalone_note_created(vault: Path) -> None:
    rec = _make_recording(name="MEETING_Weekly_Sync", file_id="c" * 32)
    writer = ObsidianWriter(vault)
    status = writer.process_recording(rec, "会議の要約", TARGET_DATE)

    assert status == "created"
    note = vault / "Notes" / "PLAUD" / "2026-06-14-MEETING_Weekly_Sync.md"
    assert note.exists()
    content = note.read_text(encoding="utf-8")
    assert "plaud_id:" in content
    assert "## 要約" in content
    assert "会議の要約" in content


def test_standalone_note_skip_if_exists(vault: Path) -> None:
    rec = _make_recording(name="MEETING_Test", file_id="d" * 32)
    writer = ObsidianWriter(vault)

    status1 = writer.process_recording(rec, "要約1", TARGET_DATE)
    status2 = writer.process_recording(rec, "要約2", TARGET_DATE)

    assert status1 == "created"
    assert status2 == "skipped"

    # ファイルが上書きされていない
    note = vault / "Notes" / "PLAUD" / "2026-06-14-MEETING_Test.md"
    assert "要約1" in note.read_text(encoding="utf-8")
    assert "要約2" not in note.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Daily Note へのリンク追記
# ---------------------------------------------------------------------------


def test_link_appended_to_daily_note(vault: Path) -> None:
    rec = _make_recording(name="SEMINAR_Pythonセミナー", file_id="e" * 32)
    writer = ObsidianWriter(vault)
    writer.process_recording(rec, "セミナー要約", TARGET_DATE)

    daily = vault / "Daily" / "2026" / "06" / "2026-06-14.md"
    content = daily.read_text(encoding="utf-8")
    assert "## Plaud" in content
    assert "SEMINAR_Pythonセミナー" in content
    assert f"plaud:{'e' * 32}" in content


def test_link_not_duplicated_on_rerun(vault: Path) -> None:
    rec = _make_recording(name="STUDY_ML", file_id="f" * 32)
    writer = ObsidianWriter(vault)
    writer.process_recording(rec, "学習ノート", TARGET_DATE)
    writer.process_recording(rec, "学習ノート", TARGET_DATE)

    daily = vault / "Daily" / "2026" / "06" / "2026-06-14.md"
    content = daily.read_text(encoding="utf-8")
    assert content.count(f"plaud:{'f' * 32}") == 1


# ---------------------------------------------------------------------------
# dry_run モード
# ---------------------------------------------------------------------------


def test_dry_run_does_not_create_files(vault: Path) -> None:
    rec = _make_recording(name="MEETING_DryRun", file_id="0" * 32)
    writer = ObsidianWriter(vault, dry_run=True)
    status = writer.process_recording(rec, "ドライラン", TARGET_DATE)

    assert status == "created"
    assert not (vault / "Notes" / "PLAUD").exists()
    assert not (vault / "Daily").exists()


def test_dry_run_idea_does_not_write(vault: Path) -> None:
    rec = _make_recording(name="IDEA_ドライラン", file_id="1" * 32)
    writer = ObsidianWriter(vault, dry_run=True)
    writer.process_recording(rec, "ドライアイデア", TARGET_DATE)

    assert not (vault / "Daily").exists()
