from __future__ import annotations

from datetime import date, datetime
from unittest.mock import patch

import pytest

from life_analytics.plaud_client import (
    PlaudAuthenticationError,
    PlaudClient,
    PlaudCLIError,
    _parse_summary,
)

# ---------------------------------------------------------------------------
# テスト用フィクスチャ
# ---------------------------------------------------------------------------

RECENT_OUTPUT = """\
- Fetching recordings from the last 2 days...

Recordings in the last 2 days: 2

  aabbccddeeff00112233445566778899  MEETING_Weekly_Sync  2026-06-13  42m05s
  7190240c21240ccfc5c38038e42c893e  2026-06-14 18:48:29テストメモ  2026-06-14  16s
"""

FILE_OUTPUT_A = """\
- Fetching file...

File Details:

  id:           aabbccddeeff00112233445566778899
  name:         MEETING_Weekly_Sync
  created_at:   2026-06-13T10:00:00
  start_at:     2026-06-13T09:58:00
  duration:     42m05s
  serial_number: 8822B50254608918
  audio:        available
  transcript:   available
  summary:      available
"""

FILE_OUTPUT_B = """\
- Fetching file...

File Details:

  id:           7190240c21240ccfc5c38038e42c893e
  name:         2026-06-14 18:48:29テストメモ
  created_at:   2026-06-14T09:49:01
  start_at:     2026-06-14T09:48:29
  duration:     16s
  serial_number: 8822B50254608918
  audio:        available
  transcript:   available
  summary:      available
"""

SUMMARY_OUTPUT = """\
- Fetching summary...

Summary: 2026-06-14 18:48:29テストメモ

これはテストの録音です。
プラウドCLIを利用してオブシダにデータ連携をするテストになります。
"""


# ---------------------------------------------------------------------------
# _parse_summary
# ---------------------------------------------------------------------------


def test_parse_summary_extracts_body() -> None:
    result = _parse_summary(SUMMARY_OUTPUT)
    assert "これはテストの録音です。" in result
    assert "プラウドCLIを利用して" in result
    assert "Summary:" not in result
    assert "Fetching" not in result


def test_parse_summary_empty_output() -> None:
    assert _parse_summary("") == ""


def test_parse_summary_no_body() -> None:
    output = "- Fetching summary...\n\nSummary: タイトル\n\n"
    assert _parse_summary(output) == ""


# ---------------------------------------------------------------------------
# fetch_recordings
# ---------------------------------------------------------------------------


def _make_client() -> PlaudClient:
    return PlaudClient("npx @plaud-ai/cli")


def _mock_run(outputs: list[str]):
    """_run の呼び出しを順番に outputs で置き換えるモック。"""
    side_effects = iter(outputs)

    def _run(self, *args):  # noqa: ANN001
        return next(side_effects)

    return patch.object(PlaudClient, "_run", _run)


def test_fetch_recordings_filters_by_date() -> None:
    with _mock_run([RECENT_OUTPUT, FILE_OUTPUT_A, FILE_OUTPUT_B]):
        client = _make_client()
        recs = client.fetch_recordings(date(2026, 6, 14))

    assert len(recs) == 1
    assert recs[0].id == "7190240c21240ccfc5c38038e42c893e"
    assert recs[0].name == "2026-06-14 18:48:29テストメモ"
    assert recs[0].duration == "16s"
    assert recs[0].start_at == datetime(2026, 6, 14, 9, 48, 29)


def test_fetch_recordings_returns_empty_when_no_match() -> None:
    with _mock_run([RECENT_OUTPUT, FILE_OUTPUT_A, FILE_OUTPUT_B]):
        client = _make_client()
        recs = client.fetch_recordings(date(2026, 6, 15))

    assert recs == []


def test_fetch_recordings_skips_failed_file(caplog) -> None:
    """file <id> の取得に失敗した録音はスキップしてログに警告を出す。"""
    call_count = 0

    def _run(self, *args):  # noqa: ANN001
        nonlocal call_count
        if call_count == 0:
            call_count += 1
            return RECENT_OUTPUT
        call_count += 1
        raise PlaudCLIError("server error")

    with patch.object(PlaudClient, "_run", _run):
        client = _make_client()
        import logging

        with caplog.at_level(logging.WARNING):
            recs = client.fetch_recordings(date(2026, 6, 14))

    assert recs == []
    assert "スキップします" in caplog.text


# ---------------------------------------------------------------------------
# fetch_summary
# ---------------------------------------------------------------------------


def test_fetch_summary_returns_body() -> None:
    with _mock_run([SUMMARY_OUTPUT]):
        client = _make_client()
        result = client.fetch_summary("7190240c21240ccfc5c38038e42c893e")

    assert "これはテストの録音です。" in result


def test_fetch_summary_returns_empty_on_error(caplog) -> None:
    def _run_raises(self, *args):  # noqa: ANN001
        raise PlaudCLIError("network error")

    with patch.object(PlaudClient, "_run", _run_raises):
        client = _make_client()
        import logging

        with caplog.at_level(logging.WARNING):
            result = client.fetch_summary("dummy_id")

    assert result == ""
    assert "要約の取得に失敗" in caplog.text


# ---------------------------------------------------------------------------
# PlaudCLIError: CLI が見つからない場合
# ---------------------------------------------------------------------------


def test_fetch_recordings_raises_on_missing_cli() -> None:
    client = PlaudClient("nonexistent-cli-command")
    with pytest.raises(PlaudCLIError, match="見つかりません"):
        client.fetch_recordings(date(2026, 6, 14))


# ---------------------------------------------------------------------------
# PlaudAuthenticationError: AUTH_FAILED 検知
# ---------------------------------------------------------------------------


def _mock_subprocess(stdout: str = "", stderr: str = "", returncode: int = 0):
    """subprocess.run の戻り値をモックするパッチ。"""
    from unittest.mock import MagicMock

    mock_result = MagicMock()
    mock_result.stdout = stdout
    mock_result.stderr = stderr
    mock_result.returncode = returncode
    return patch("subprocess.run", return_value=mock_result)


def test_auth_failed_in_stdout_raises_authentication_error() -> None:
    """stdout に AUTH_FAILED が含まれる場合 PlaudAuthenticationError を raise する。"""
    with _mock_subprocess(stdout="AUTH_FAILED\nToken invalid or expired."):
        client = PlaudClient("plaud")
        with pytest.raises(PlaudAuthenticationError, match="plaud login"):
            client.fetch_recordings(date(2026, 6, 14))


def test_auth_failed_in_stderr_raises_authentication_error() -> None:
    """stderr に AUTH_FAILED が含まれる場合 PlaudAuthenticationError を raise する。"""
    with _mock_subprocess(stderr="AUTH_FAILED\nToken invalid or expired.", returncode=1):
        client = PlaudClient("plaud")
        with pytest.raises(PlaudAuthenticationError, match="plaud login"):
            client.fetch_recordings(date(2026, 6, 14))


def test_auth_failed_is_subclass_of_plaud_cli_error() -> None:
    """PlaudAuthenticationError は PlaudCLIError のサブクラスである。"""
    assert issubclass(PlaudAuthenticationError, PlaudCLIError)


def test_fetch_summary_propagates_auth_error() -> None:
    """fetch_summary は PlaudAuthenticationError を握りつぶさず伝播する。"""
    with _mock_subprocess(stdout="AUTH_FAILED\nToken invalid or expired."):
        client = PlaudClient("plaud")
        with pytest.raises(PlaudAuthenticationError):
            client.fetch_summary("dummy_id")


# ---------------------------------------------------------------------------
# タイムアウト
# ---------------------------------------------------------------------------


def test_timeout_raises_plaud_cli_error() -> None:
    """`subprocess.TimeoutExpired` が `PlaudCLIError` に変換される。"""
    import subprocess
    from unittest.mock import patch as _patch

    with _patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="plaud", timeout=5)):
        client = PlaudClient("plaud", timeout=5)
        with pytest.raises(PlaudCLIError, match="タイムアウト"):
            client.fetch_recordings(date(2026, 6, 14))


# ---------------------------------------------------------------------------
# 正常系: timeout 付き PlaudClient
# ---------------------------------------------------------------------------


def test_fetch_recordings_with_timeout() -> None:
    """timeout を指定した PlaudClient でも録音を正常取得できる。"""
    with _mock_run([RECENT_OUTPUT, FILE_OUTPUT_A, FILE_OUTPUT_B]):
        client = PlaudClient("npx @plaud-ai/cli", timeout=30)
        recs = client.fetch_recordings(date(2026, 6, 14))

    assert len(recs) == 1
    assert recs[0].id == "7190240c21240ccfc5c38038e42c893e"
