from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_DEFAULT_TIMEOUT = 60


@dataclass(frozen=True)
class Config:
    vault_path: Path
    plaud_cli: str
    plaud_timeout: int
    log_level: str


def load_config() -> Config:
    load_dotenv()

    vault_path_str = os.environ.get("OBSIDIAN_VAULT_PATH")
    if not vault_path_str:
        raise ValueError(
            "OBSIDIAN_VAULT_PATH が未設定です。.env または環境変数に設定してください。"
        )

    vault_path = Path(vault_path_str).expanduser().resolve()
    if not vault_path.is_dir():
        raise ValueError(
            f"OBSIDIAN_VAULT_PATH が存在しないか、ディレクトリではありません: {vault_path}"
        )

    timeout_str = os.environ.get("PLAUD_TIMEOUT", str(_DEFAULT_TIMEOUT))
    try:
        plaud_timeout = int(timeout_str)
        if plaud_timeout <= 0:
            raise ValueError
    except ValueError:
        raise ValueError(
            f"PLAUD_TIMEOUT は正の整数で指定してください（現在の値: {timeout_str!r}）"
        )

    return Config(
        vault_path=vault_path,
        plaud_cli=os.environ.get("PLAUD_CLI", "npx @plaud-ai/cli"),
        plaud_timeout=plaud_timeout,
        log_level=os.environ.get("LOG_LEVEL", "INFO"),
    )
