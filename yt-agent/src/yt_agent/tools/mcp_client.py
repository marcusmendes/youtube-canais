"""Async MCP client wrappers for VidIQ (Streamable HTTP) and YouTube (stdio)."""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from typing import Any

import httpx
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamable_http_client
from mcp.types import TextContent

logger = logging.getLogger(__name__)


def _extract_text(result: Any) -> str:
    """Pull the text payload from an MCP CallToolResult."""
    for block in result.content:
        if isinstance(block, TextContent):
            return block.text
    return ""


def _parse_result(result: Any) -> dict[str, Any] | list[Any]:
    """Parse an MCP CallToolResult into a dict or list."""
    if result.isError:
        texts = [b.text for b in result.content if isinstance(b, TextContent)]
        msg = " ".join(texts) or "MCP tool returned an error"
        raise RuntimeError(msg)

    if result.structuredContent:
        return result.structuredContent

    raw = _extract_text(result)
    if not raw:
        return {}
    return json.loads(raw)


@asynccontextmanager
async def vidiq_session(url: str, bearer_token: str):
    """Open an MCP session to the VidIQ Streamable HTTP server.

    Yields a ``ClientSession`` ready for ``call_tool()``.
    """
    http = httpx.AsyncClient(
        headers={"Authorization": f"Bearer {bearer_token}"},
        timeout=60.0,
    )
    try:
        async with (
            streamable_http_client(url, http_client=http) as (read, write, _),
            ClientSession(read, write) as session,
        ):
            await session.initialize()
            yield session
    finally:
        await http.aclose()


@asynccontextmanager
async def youtube_session(command: str, env: dict[str, str] | None = None):
    """Open an MCP session to the YouTube stdio server.

    Yields a ``ClientSession`` ready for ``call_tool()``.
    """
    params = StdioServerParameters(command=command, env=env)
    async with (
        stdio_client(params) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        yield session
