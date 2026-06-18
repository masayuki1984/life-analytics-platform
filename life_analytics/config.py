from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    vault_path: Path
    plaud_cli: str
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

    return Config(
        vault_path=vault_path,
        plaud_cli=os.environ.get("PLAUD_CLI", "npx @plaud-ai/cli"),
        log_level=os.environ.get("LOG_LEVEL", "INFO"),
    )
