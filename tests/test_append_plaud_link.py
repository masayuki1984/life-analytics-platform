from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from life_analytics.obsidian.append_plaud_link import (
    PlaudNoteInfo,
    append_plaud_link,
    append_to_plaud_section,
    collect_plaud_notes,
    format_link_entry,
    parse_plaud_note,
)

TARGET_DATE = date(2026, 6, 22)
PLAUD_ID = "aabbccddeeff00112233445566778899"

DAILY_WITH_PLAUD_SECTION = """\
# 2026-06-22

## 今日の目標

-

## Plaud

## メモ

メモ内容
"""

DAILY_WITHOUT_PLAUD_SECTION = """\
# 2026-06-22

## 今日の目標

-

## メモ
"""

PLAUD_NOTE_CONTENT = f"""\
---
plaud_id: {PLAUD_ID}
date: 2026-06-22
duration: 42m05s
source: plaud
---

# MEETING_Weekly_Sync

会議の内容
"""


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    return tmp_path


def _make_daily_note(vault: Path, d: date, content: str) -> Path:
    path = vault / "Daily" / f"{d.year:04d}" / f"{d.month:02d}" / f"{d.isoformat()}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _make_plaud_note(
    vault: Path,
    d: date,
    filename: str,
    content: str,
) -> Path:
    plaud_dir = vault / "Notes" / "PLAUD"
    plaud_dir.mkdir(parents=True, exist_ok=True)
    path = plaud_dir / f"{d.isoformat()}-{filename}.md"
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# parse_plaud_note
# ---------------------------------------------------------------------------


def test_parse_plaud_note_extracts_fields(vault: Path) -> None:
    path = _make_plaud_note(vault, TARGET_DATE, "MEETING_Weekly_Sync", PLAUD_NOTE_CONTENT)
    info = parse_plaud_note(path, vault)
    assert info is not None
    assert info.plaud_id == PLAUD_ID
    assert info.name == "MEETING_Weekly_Sync"
    assert info.duration == "42m05s"


def test_parse_plaud_note_returns_none_when_no_frontmatter(vault: Path) -> None:
    path = _make_plaud_note(vault, TARGET_DATE, "no_fm", "# Title\n内容\n")
    assert parse_plaud_note(path, vault) is None


def test_parse_plaud_note_returns_none_when_no_heading(vault: Path) -> None:
    content = "---\nplaud_id: abc\nduration: 1m\nsource: plaud\n---\n\n内容\n"
    path = _make_plaud_note(vault, TARGET_DATE, "no_heading", content)
    assert parse_plaud_note(path, vault) is None


# ---------------------------------------------------------------------------
# collect_plaud_notes
# ---------------------------------------------------------------------------


def test_collect_plaud_notes_returns_notes_for_date(vault: Path) -> None:
    _make_plaud_note(vault, TARGET_DATE, "MEETING_foo", PLAUD_NOTE_CONTENT)
    notes = collect_plaud_notes(vault, TARGET_DATE)
    assert len(notes) == 1
    assert notes[0].plaud_id == PLAUD_ID


def test_collect_plaud_notes_excludes_other_dates(vault: Path) -> None:
    other_date = date(2026, 6, 20)
    _make_plaud_note(vault, other_date, "MEETING_old", PLAUD_NOTE_CONTENT)
    notes = collect_plaud_notes(vault, TARGET_DATE)
    assert notes == []


def test_collect_plaud_notes_returns_empty_when_dir_missing(vault: Path) -> None:
    notes = collect_plaud_notes(vault, TARGET_DATE)
    assert notes == []


# ---------------------------------------------------------------------------
# format_link_entry
# ---------------------------------------------------------------------------


def test_format_link_entry_contains_wikilink(vault: Path) -> None:
    path = vault / "Notes" / "PLAUD" / "2026-06-22-MEETING_foo.md"
    info = PlaudNoteInfo(path=path, plaud_id=PLAUD_ID, name="MEETING_foo", duration="5m")
    entry = format_link_entry(info, vault)
    assert "[[Notes/PLAUD/2026-06-22-MEETING_foo|MEETING_foo]]" in entry
    assert f"plaud:{PLAUD_ID}" in entry
    assert "5m" in entry


def test_format_link_entry_no_duration(vault: Path) -> None:
    path = vault / "Notes" / "PLAUD" / "2026-06-22-foo.md"
    info = PlaudNoteInfo(path=path, plaud_id=PLAUD_ID, name="foo", duration="")
    entry = format_link_entry(info, vault)
    assert "[[Notes/PLAUD/2026-06-22-foo|foo]]" in entry
    assert " — " not in entry


# ---------------------------------------------------------------------------
# append_to_plaud_section
# ---------------------------------------------------------------------------


def test_append_to_plaud_section_inserts_before_next_section() -> None:
    content = DAILY_WITH_PLAUD_SECTION
    entry = "- [[Notes/PLAUD/foo|foo]] — 5m\n  <!-- plaud:abc -->"
    result = append_to_plaud_section(content, entry)

    lines = result.splitlines()
    plaud_idx = lines.index("## Plaud")
    memo_idx = lines.index("## メモ")
    entry_idx = next(i for i, line in enumerate(lines) if "[[Notes/PLAUD/foo" in line)

    assert plaud_idx < entry_idx < memo_idx


def test_append_to_plaud_section_appends_at_end_when_last_section() -> None:
    content = "# Title\n\n## Plaud\n\n"
    entry = "- [[Notes/PLAUD/foo|foo]]\n  <!-- plaud:abc -->"
    result = append_to_plaud_section(content, entry)
    assert "[[Notes/PLAUD/foo" in result


def test_append_to_plaud_section_no_change_when_no_plaud() -> None:
    content = "# Title\n\n## メモ\n\n内容\n"
    result = append_to_plaud_section(content, "エントリ")
    assert result == content


def test_append_to_plaud_section_multiple_entries() -> None:
    content = DAILY_WITH_PLAUD_SECTION
    entry1 = "- [[Notes/PLAUD/foo|foo]]\n  <!-- plaud:id1 -->"
    entry2 = "- [[Notes/PLAUD/bar|bar]]\n  <!-- plaud:id2 -->"
    result = append_to_plaud_section(content, entry1)
    result = append_to_plaud_section(result, entry2)

    assert "foo" in result
    assert "bar" in result
    lines = result.splitlines()
    memo_idx = lines.index("## メモ")
    assert all(lines.index(line) < memo_idx for line in lines if "[[Notes/PLAUD/" in line)


# ---------------------------------------------------------------------------
# append_plaud_link (integration)
# ---------------------------------------------------------------------------


def test_append_plaud_link_appends_link(vault: Path) -> None:
    _make_daily_note(vault, TARGET_DATE, DAILY_WITH_PLAUD_SECTION)
    _make_plaud_note(vault, TARGET_DATE, "MEETING_Weekly_Sync", PLAUD_NOTE_CONTENT)

    status = append_plaud_link(vault, TARGET_DATE)
    assert status == "appended"

    daily_path = vault / "Daily" / "2026" / "06" / "2026-06-22.md"
    content = daily_path.read_text(encoding="utf-8")
    assert "MEETING_Weekly_Sync" in content
    assert f"plaud:{PLAUD_ID}" in content


def test_append_plaud_link_skips_when_no_daily_note(vault: Path) -> None:
    status = append_plaud_link(vault, TARGET_DATE)
    assert status == "skipped_no_note"


def test_append_plaud_link_skips_when_no_plaud_section(vault: Path) -> None:
    _make_daily_note(vault, TARGET_DATE, DAILY_WITHOUT_PLAUD_SECTION)
    _make_plaud_note(vault, TARGET_DATE, "MEETING_foo", PLAUD_NOTE_CONTENT)

    status = append_plaud_link(vault, TARGET_DATE)
    assert status == "skipped_no_section"


def test_append_plaud_link_idempotent(vault: Path) -> None:
    _make_daily_note(vault, TARGET_DATE, DAILY_WITH_PLAUD_SECTION)
    _make_plaud_note(vault, TARGET_DATE, "MEETING_Weekly_Sync", PLAUD_NOTE_CONTENT)

    append_plaud_link(vault, TARGET_DATE)
    status2 = append_plaud_link(vault, TARGET_DATE)
    assert status2 == "no_new_links"

    daily_path = vault / "Daily" / "2026" / "06" / "2026-06-22.md"
    content = daily_path.read_text(encoding="utf-8")
    assert content.count(f"plaud:{PLAUD_ID}") == 1


def test_append_plaud_link_no_new_links_when_no_plaud_notes(vault: Path) -> None:
    _make_daily_note(vault, TARGET_DATE, DAILY_WITH_PLAUD_SECTION)
    status = append_plaud_link(vault, TARGET_DATE)
    assert status == "no_new_links"
