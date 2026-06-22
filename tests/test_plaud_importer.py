from __future__ import annotations

import sys
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

from life_analytics.plaud_client import PlaudAuthenticationError, PlaudRecording


def _make_recording(name: str = "MEETING_Test", file_id: str = "a" * 32) -> PlaudRecording:
    return PlaudRecording(
        id=file_id,
        name=name,
        start_at=datetime(2026, 6, 14, 10, 0, 0),
        created_at=datetime(2026, 6, 14, 10, 0, 0),
        duration="5m00s",
    )


# ---------------------------------------------------------------------------
# parse_args
# ---------------------------------------------------------------------------


def test_parse_args_default_no_date(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["plaud_importer"])
    from life_analytics.plaud_importer import parse_args

    args = parse_args()
    assert args.date is None
    assert args.dry_run is False


def test_parse_args_with_date(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["plaud_importer", "--date", "2026-06-14"])
    from life_analytics.plaud_importer import parse_args

    args = parse_args()
    assert args.date == date(2026, 6, 14)


def test_parse_args_dry_run(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["plaud_importer", "--dry-run"])
    from life_analytics.plaud_importer import parse_args

    args = parse_args()
    assert args.dry_run is True


# ---------------------------------------------------------------------------
# main() オーケストレーション
# ---------------------------------------------------------------------------


def test_main_exits_1_on_missing_env(monkeypatch, tmp_path) -> None:
    """OBSIDIAN_VAULT_PATH 未設定で exit 1 になる。"""
    monkeypatch.setattr(sys, "argv", ["plaud_importer"])
    monkeypatch.delenv("OBSIDIAN_VAULT_PATH", raising=False)

    from life_analytics.plaud_importer import main

    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1


def test_main_success(monkeypatch, tmp_path) -> None:
    """録音が 1 件あり正常処理された場合に exit 0 で終了する。"""
    monkeypatch.setattr(sys, "argv", ["plaud_importer", "--date", "2026-06-14"])
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(tmp_path))

    rec = _make_recording()

    mock_client = MagicMock()
    mock_client.fetch_recordings.return_value = [rec]
    mock_client.fetch_summary.return_value = "テスト要約"

    mock_writer = MagicMock()
    mock_writer.process_recording.return_value = "created"

    with (
        patch("life_analytics.plaud_importer.PlaudClient", return_value=mock_client),
        patch("life_analytics.plaud_importer.ObsidianWriter", return_value=mock_writer),
    ):
        from life_analytics import plaud_importer

        # main() が SystemExit を raise しないことを確認
        try:
            plaud_importer.main()
        except SystemExit as e:
            pytest.fail(f"main() が予期せず exit {e.code} しました")

    mock_writer.ensure_daily_note.assert_called_once_with(date(2026, 6, 14))


def test_main_creates_daily_note_when_no_recordings(monkeypatch, tmp_path) -> None:
    """録音が 0 件でも Daily Note が作成される。"""
    monkeypatch.setattr(sys, "argv", ["plaud_importer", "--date", "2026-06-14"])
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(tmp_path))

    mock_client = MagicMock()
    mock_client.fetch_recordings.return_value = []

    mock_writer = MagicMock()

    with (
        patch("life_analytics.plaud_importer.PlaudClient", return_value=mock_client),
        patch("life_analytics.plaud_importer.ObsidianWriter", return_value=mock_writer),
    ):
        from life_analytics import plaud_importer

        try:
            plaud_importer.main()
        except SystemExit as e:
            pytest.fail(f"main() が予期せず exit {e.code} しました")

    mock_writer.ensure_daily_note.assert_called_once_with(date(2026, 6, 14))
    mock_writer.write_no_recordings.assert_called_once_with(date(2026, 6, 14))
    mock_writer.process_recording.assert_not_called()


def test_main_exits_1_on_auth_error_in_fetch_recordings(monkeypatch, tmp_path) -> None:
    """fetch_recordings が PlaudAuthenticationError を raise したとき exit 1 になる。"""
    monkeypatch.setattr(sys, "argv", ["plaud_importer", "--date", "2026-06-14"])
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(tmp_path))

    mock_client = MagicMock()
    mock_client.fetch_recordings.side_effect = PlaudAuthenticationError("認証エラー")

    mock_writer = MagicMock()

    with (
        patch("life_analytics.plaud_importer.PlaudClient", return_value=mock_client),
        patch("life_analytics.plaud_importer.ObsidianWriter", return_value=mock_writer),
    ):
        from life_analytics import plaud_importer

        with pytest.raises(SystemExit) as exc:
            plaud_importer.main()
        assert exc.value.code == 1


def test_main_exits_1_on_auth_error_in_fetch_summary(monkeypatch, tmp_path) -> None:
    """fetch_summary が PlaudAuthenticationError を raise したとき exit 1 になる。"""
    monkeypatch.setattr(sys, "argv", ["plaud_importer", "--date", "2026-06-14"])
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(tmp_path))

    rec = _make_recording()

    mock_client = MagicMock()
    mock_client.fetch_recordings.return_value = [rec]
    mock_client.fetch_summary.side_effect = PlaudAuthenticationError("認証エラー")

    mock_writer = MagicMock()

    with (
        patch("life_analytics.plaud_importer.PlaudClient", return_value=mock_client),
        patch("life_analytics.plaud_importer.ObsidianWriter", return_value=mock_writer),
    ):
        from life_analytics import plaud_importer

        with pytest.raises(SystemExit) as exc:
            plaud_importer.main()
        assert exc.value.code == 1


def test_main_exits_1_on_all_failed(monkeypatch, tmp_path) -> None:
    """全録音の処理が失敗した場合に exit 1 になる。"""
    monkeypatch.setattr(sys, "argv", ["plaud_importer", "--date", "2026-06-14"])
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(tmp_path))

    rec = _make_recording()

    mock_client = MagicMock()
    mock_client.fetch_recordings.return_value = [rec]
    mock_client.fetch_summary.return_value = ""

    mock_writer = MagicMock()
    mock_writer.process_recording.side_effect = RuntimeError("書き込みエラー")

    with (
        patch("life_analytics.plaud_importer.PlaudClient", return_value=mock_client),
        patch("life_analytics.plaud_importer.ObsidianWriter", return_value=mock_writer),
    ):
        from life_analytics import plaud_importer

        with pytest.raises(SystemExit) as exc:
            plaud_importer.main()
        assert exc.value.code == 1
