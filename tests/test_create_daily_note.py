from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from life_analytics.obsidian.create_daily_note import (
    create_daily_note,
    get_daily_note_path,
    get_template_content,
    load_vault_root,
)

TARGET_DATE = date(2026, 6, 23)
TEMPLATE_CONTENT = "# {{date}}\n\n## 今日の目標\n\n-\n\n## Plaud\n\n## メモ\n"


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def vault_with_template(vault: Path) -> Path:
    template_dir = vault / "Templates"
    template_dir.mkdir(parents=True)
    (template_dir / "daily.md").write_text(TEMPLATE_CONTENT, encoding="utf-8")
    return vault


# ---------------------------------------------------------------------------
# get_daily_note_path
# ---------------------------------------------------------------------------


def test_daily_note_path_structure(vault: Path) -> None:
    path = get_daily_note_path(vault, TARGET_DATE)
    assert path == vault / "Daily" / "2026" / "06" / "2026-06-23.md"


# ---------------------------------------------------------------------------
# get_template_content
# ---------------------------------------------------------------------------


def test_get_template_content_reads_file(vault_with_template: Path) -> None:
    content = get_template_content(vault_with_template)
    assert content == TEMPLATE_CONTENT


def test_get_template_content_raises_when_missing(vault: Path) -> None:
    with pytest.raises(FileNotFoundError, match="テンプレートファイルが存在しません"):
        get_template_content(vault)


# ---------------------------------------------------------------------------
# create_daily_note
# ---------------------------------------------------------------------------


def test_create_daily_note_copies_template(vault_with_template: Path) -> None:
    status = create_daily_note(vault_with_template, TARGET_DATE)
    assert status == "created"

    path = get_daily_note_path(vault_with_template, TARGET_DATE)
    assert path.exists()
    assert path.read_text(encoding="utf-8") == TEMPLATE_CONTENT


def test_create_daily_note_creates_parent_dirs(vault_with_template: Path) -> None:
    create_daily_note(vault_with_template, TARGET_DATE)
    assert (vault_with_template / "Daily" / "2026" / "06").is_dir()


def test_create_daily_note_skips_if_exists(vault_with_template: Path) -> None:
    path = get_daily_note_path(vault_with_template, TARGET_DATE)
    path.parent.mkdir(parents=True)
    path.write_text("既存コンテンツ", encoding="utf-8")

    status = create_daily_note(vault_with_template, TARGET_DATE)
    assert status == "skipped"
    assert path.read_text(encoding="utf-8") == "既存コンテンツ"


def test_create_daily_note_idempotent(vault_with_template: Path) -> None:
    status1 = create_daily_note(vault_with_template, TARGET_DATE)
    status2 = create_daily_note(vault_with_template, TARGET_DATE)
    assert status1 == "created"
    assert status2 == "skipped"


def test_create_daily_note_raises_when_no_template(vault: Path) -> None:
    with pytest.raises(FileNotFoundError):
        create_daily_note(vault, TARGET_DATE)


# ---------------------------------------------------------------------------
# load_vault_root
# ---------------------------------------------------------------------------


def test_load_vault_root_reads_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("OBSIDIAN_VAULT_ROOT", str(tmp_path))
    result = load_vault_root()
    assert result == tmp_path.resolve()


def test_load_vault_root_raises_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OBSIDIAN_VAULT_ROOT", raising=False)
    with pytest.raises(ValueError, match="OBSIDIAN_VAULT_ROOT が未設定"):
        load_vault_root()
