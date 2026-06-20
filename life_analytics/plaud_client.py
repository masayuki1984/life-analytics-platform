from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass
from datetime import date, datetime

logger = logging.getLogger(__name__)

# 32 文字の hex ID（録音 ID の形式）
_ID_RE = re.compile(r"\b([0-9a-f]{32})\b")

# "  key:   value" 形式のパーサー
_KV_RE = re.compile(r"^\s+(\w+):\s+(.+)$")

# 認証失敗パターン（stdout/stderr いずれかに含まれていれば即終了）
_AUTH_FAILED_RE = re.compile(r"AUTH_FAILED")


@dataclass
class PlaudRecording:
    id: str
    name: str
    start_at: datetime
    created_at: datetime
    duration: str  # CLI から整形済みで返る ("16s", "5m23s" 等)


class PlaudCLIError(Exception):
    pass


class PlaudAuthenticationError(PlaudCLIError):
    """Plaud CLI の認証トークンが無効または期限切れ。"""

    pass


class PlaudClient:
    def __init__(self, cli: str, timeout: int = 60) -> None:
        self._cli = cli
        self._timeout = timeout

    def _run(self, *args: str) -> str:
        cmd = self._cli.split() + list(args)
        cmd_str = " ".join(cmd)
        t0 = datetime.now()
        logger.debug("Plaud CLI 開始: %s  [%s]", cmd_str, t0.strftime("%H:%M:%S"))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=self._timeout,
            )
        except FileNotFoundError as e:
            raise PlaudCLIError(f"Plaud CLI が見つかりません: {self._cli}") from e
        except subprocess.TimeoutExpired as e:
            raise PlaudCLIError(
                f"Plaud CLI がタイムアウトしました ({self._timeout}s): {cmd_str}"
            ) from e
        finally:
            elapsed = (datetime.now() - t0).total_seconds()
            logger.debug("Plaud CLI 終了: %s  経過 %.1fs", cmd_str, elapsed)

        # AUTH_FAILED は returncode チェックより先に判定する
        combined = result.stdout + result.stderr
        if _AUTH_FAILED_RE.search(combined):
            raise PlaudAuthenticationError(
                "Plaud CLI の認証が期限切れです。`plaud login` を実行してください。"
            )

        if result.returncode != 0:
            raise PlaudCLIError(
                f"Plaud CLI がエラーで終了しました (exit {result.returncode}): "
                f"{result.stderr.strip()}"
            )

        return result.stdout

    def fetch_recordings(self, target_date: date) -> list[PlaudRecording]:
        """対象日の録音一覧を返す。"""
        today = date.today()
        elapsed = (today - target_date).days
        days = max(2, elapsed + 2)

        output = self._run("recent", "--days", str(days))
        ids = _ID_RE.findall(output)

        recordings: list[PlaudRecording] = []
        for file_id in ids:
            try:
                rec = self._fetch_file_detail(file_id)
                if rec.start_at.date() == target_date:
                    recordings.append(rec)
            except PlaudAuthenticationError:
                raise  # 認証エラーは上位へ伝播
            except PlaudCLIError as e:
                logger.warning(f"録音 {file_id} の取得をスキップします: {e}")

        return recordings

    def _fetch_file_detail(self, file_id: str) -> PlaudRecording:
        """`file <id>` コマンドの出力をパースして PlaudRecording を返す。"""
        output = self._run("file", file_id)
        kv: dict[str, str] = {}
        for line in output.splitlines():
            m = _KV_RE.match(line)
            if m:
                kv[m.group(1)] = m.group(2).strip()

        try:
            return PlaudRecording(
                id=kv["id"],
                name=kv["name"],
                start_at=datetime.fromisoformat(kv["start_at"]),
                created_at=datetime.fromisoformat(kv["created_at"]),
                duration=kv["duration"],
            )
        except KeyError as e:
            raise PlaudCLIError(f"file コマンドの出力にフィールドがありません: {e}") from e

    def fetch_summary(self, file_id: str) -> str:
        """録音の AI 要約を返す。認証エラーは伝播、それ以外の失敗は空文字列を返す。"""
        try:
            output = self._run("summary", file_id)
            return _parse_summary(output)
        except PlaudAuthenticationError:
            raise  # 認証エラーは握りつぶさない
        except Exception as e:
            logger.warning(f"要約の取得に失敗しました [{file_id}]: {e}")
            return ""


def _parse_summary(output: str) -> str:
    """summary コマンドの出力から本文テキストを抽出する。

    出力形式:
        - Fetching summary...

        Summary: {name}

        {actual summary content}
    """
    lines = output.splitlines()
    past_header = False
    content_lines: list[str] = []

    for line in lines:
        if not past_header:
            if line.startswith("Summary:"):
                past_header = True
            continue
        # タイトル直後の空行をスキップ
        if not content_lines and line.strip() == "":
            continue
        content_lines.append(line)

    return "\n".join(content_lines).strip()
