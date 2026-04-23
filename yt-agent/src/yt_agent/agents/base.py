"""Shared utilities for all agents — prompt loading, LLM invocation, JSON parsing."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, ValidationError

from yt_agent.config import get_settings

if TYPE_CHECKING:
    from langchain_core.tools import StructuredTool

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

PROMPT_DIR = Path(__file__).parent.parent / "prompts"
MAX_ARG_DISPLAY = 80

RETRY_DELAYS = (2.0, 4.0, 8.0)
LLM_TIMEOUT_SONNET = 600.0
LLM_TIMEOUT_OPUS = 600.0


def load_prompt(filename: str) -> str:
    """Read a system prompt from the prompts/ directory."""
    path = PROMPT_DIR / filename
    return path.read_text(encoding="utf-8")


def get_sonnet() -> ChatAnthropic:
    settings = get_settings()
    return ChatAnthropic(
        model=settings.sonnet_model,
        api_key=settings.anthropic_api_key.get_secret_value(),
        max_tokens=4096,
        default_request_timeout=LLM_TIMEOUT_SONNET,
    )


def get_opus() -> ChatAnthropic:
    settings = get_settings()
    return ChatAnthropic(
        model=settings.opus_model,
        api_key=settings.anthropic_api_key.get_secret_value(),
        max_tokens=8192,
        default_request_timeout=LLM_TIMEOUT_OPUS,
    )


def _summarize_args(args: dict) -> str:
    """Compact representation of tool call arguments for logging."""
    raw = json.dumps(args, ensure_ascii=False)
    if len(raw) <= MAX_ARG_DISPLAY:
        return raw
    return raw[:MAX_ARG_DISPLAY] + "…"


async def _invoke_with_retry(
    model: ChatAnthropic,
    messages: list,
    *,
    max_api_retries: int = 3,
):
    """Invoke an LLM with exponential backoff on transient failures."""
    for attempt in range(max_api_retries):
        try:
            return await model.ainvoke(messages)
        except Exception as exc:
            is_retryable = _is_retryable_error(exc)
            if not is_retryable or attempt >= max_api_retries - 1:
                raise
            delay = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]
            logger.warning(
                "API call failed (attempt %d/%d), retrying in %.1fs: %s",
                attempt + 1, max_api_retries, delay, exc,
            )
            await asyncio.sleep(delay)
    raise RuntimeError("Unreachable")  # pragma: no cover


def _is_retryable_error(exc: Exception) -> bool:
    """Determine if an exception warrants a retry."""
    import httpx

    if isinstance(exc, httpx.TimeoutException | httpx.ConnectError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (429, 500, 502, 503, 529)
    exc_name = type(exc).__name__.lower()
    return any(k in exc_name for k in ("timeout", "rate", "overload", "529"))


async def invoke_agent_with_tools[T: BaseModel](
    *,
    system_prompt: str,
    user_message: str,
    tools: list[StructuredTool],
    llm: ChatAnthropic | None = None,
    output_schema: type[T],
    max_retries: int = 2,
    max_api_retries: int = 3,
) -> T:
    """Run an agent loop: LLM calls tools, then returns structured JSON.

    The LLM is bound to the tools and can make multiple tool calls.
    After tool execution, the final response is parsed into the output schema.

    Retry strategy:
    - API failures (timeouts, rate-limits, 5xx): exponential backoff (2s/4s/8s)
    - JSON parse failures: re-prompt with Pydantic error (up to max_retries)
    """
    if llm is None:
        llm = get_sonnet()

    model_with_tools = llm.bind_tools(tools) if tools else llm

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]

    tool_map = {t.name: t for t in tools}

    for attempt in range(max_retries + 1):
        logger.info("Calling LLM (attempt %d)...", attempt + 1)
        print(f"  [LLM] Calling {llm.model}...", flush=True)  # noqa: T201
        response = await _invoke_with_retry(
            model_with_tools, messages, max_api_retries=max_api_retries
        )
        messages.append(response)

        tool_round = 0
        while response.tool_calls:
            tool_round += 1
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool = tool_map.get(tool_name)
                if tool is None:
                    logger.warning("Unknown tool call: %s", tool_name)
                    result = f"Error: tool '{tool_name}' not found"
                else:
                    print(f"  [Tool] {tool_name}({_summarize_args(tool_args)})", flush=True)  # noqa: T201
                    try:
                        result = await tool.ainvoke(tool_args)
                        if isinstance(result, BaseModel):
                            result = result.model_dump_json()
                        elif not isinstance(result, str):
                            result = json.dumps(
                                result, default=str, ensure_ascii=False
                            )
                        print(f"  [Tool] {tool_name} ✓", flush=True)  # noqa: T201
                    except Exception as exc:
                        logger.warning("Tool %s failed: %s", tool_name, exc)
                        print(f"  [Tool] {tool_name} ✗ {exc!s:.120}", flush=True)  # noqa: T201
                        result = f"Error calling {tool_name}: {exc}"

                from langchain_core.messages import ToolMessage

                messages.append(
                    ToolMessage(
                        content=str(result), tool_call_id=tool_call["id"]
                    )
                )

            print(f"  [LLM] Processing tool results (round {tool_round})...", flush=True)  # noqa: T201
            response = await _invoke_with_retry(
                model_with_tools, messages, max_api_retries=max_api_retries
            )
            messages.append(response)

        content = response.content
        if isinstance(content, list):
            content = "\n".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in content
            )

        try:
            return _parse_json_output(content, output_schema)
        except (ValidationError, ValueError) as exc:
            if attempt < max_retries:
                logger.info(
                    "Retry %d/%d — JSON parsing failed: %s",
                    attempt + 1, max_retries, exc,
                )
                messages.append(
                    HumanMessage(
                        content=(
                            f"Your previous response could not be parsed as "
                            f"valid JSON for the schema "
                            f"{output_schema.__name__}. Error: {exc}\n\n"
                            f"Please respond with ONLY the valid JSON object, "
                            f"no markdown fences, no explanation — just the "
                            f"raw JSON."
                        )
                    )
                )
            else:
                raise


def _parse_json_output[T: BaseModel](text: str, schema: type[T]) -> T:
    """Extract and validate a JSON object from LLM text output."""
    # Strip markdown code fences if present
    cleaned = text.strip()
    if cleaned.startswith("```"):
        first_newline = cleaned.index("\n")
        cleaned = cleaned[first_newline + 1 :]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

    # Find the outermost JSON object
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        msg = f"No JSON object found in response: {cleaned[:200]}"
        raise ValueError(msg)

    json_str = cleaned[start : end + 1]
    data = json.loads(json_str)
    return schema.model_validate(data)
