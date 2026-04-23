from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: SecretStr

    # Channel identity
    channel_handle: str = "@MarcusMacielIAeCiencia"

    # VidIQ MCP (Streamable HTTP)
    vidiq_mcp_url: str = "https://mcp.vidiq.com/mcp"
    vidiq_api_key: SecretStr = SecretStr("")

    # YouTube MCP (stdio)
    youtube_mcp_command: str = "zubeid-youtube-mcp-server"
    youtube_api_key: SecretStr = SecretStr("")
    google_client_secret_path: str = ""

    database_url: str = "sqlite+aiosqlite:///data/yt_agent.db"

    prompt_dir: Path = Path("../canais/marcus-maciel/prompts/")
    models_dir: Path = Path("../canais/marcus-maciel/modelos-de-escrita/")

    sonnet_model: str = "claude-sonnet-4-20250514"
    opus_model: str = "claude-opus-4-20250514"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
