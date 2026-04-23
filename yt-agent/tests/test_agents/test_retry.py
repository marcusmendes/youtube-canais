"""Tests for retry and error handling logic in agent base utilities.

Sprint 6.3: Covers exponential backoff, retryable error detection, and JSON retry.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from yt_agent.agents.base import (
    _invoke_with_retry,
    _is_retryable_error,
)
from yt_agent.state import ThemeValidation

# ── _is_retryable_error ─────────────────────────────────────────────


class TestRetryableErrors:
    def test_timeout_is_retryable(self):
        exc = httpx.ReadTimeout("timed out")
        assert _is_retryable_error(exc) is True

    def test_connect_error_is_retryable(self):
        exc = httpx.ConnectError("connection refused")
        assert _is_retryable_error(exc) is True

    def test_429_is_retryable(self):
        response = MagicMock()
        response.status_code = 429
        exc = httpx.HTTPStatusError("rate limit", request=MagicMock(), response=response)
        assert _is_retryable_error(exc) is True

    def test_500_is_retryable(self):
        response = MagicMock()
        response.status_code = 500
        exc = httpx.HTTPStatusError("server", request=MagicMock(), response=response)
        assert _is_retryable_error(exc) is True

    def test_502_is_retryable(self):
        response = MagicMock()
        response.status_code = 502
        exc = httpx.HTTPStatusError("bad gw", request=MagicMock(), response=response)
        assert _is_retryable_error(exc) is True

    def test_503_is_retryable(self):
        response = MagicMock()
        response.status_code = 503
        exc = httpx.HTTPStatusError("unavailable", request=MagicMock(), response=response)
        assert _is_retryable_error(exc) is True

    def test_529_is_retryable(self):
        response = MagicMock()
        response.status_code = 529
        exc = httpx.HTTPStatusError("overloaded", request=MagicMock(), response=response)
        assert _is_retryable_error(exc) is True

    def test_400_not_retryable(self):
        response = MagicMock()
        response.status_code = 400
        exc = httpx.HTTPStatusError("bad request", request=MagicMock(), response=response)
        assert _is_retryable_error(exc) is False

    def test_401_not_retryable(self):
        response = MagicMock()
        response.status_code = 401
        exc = httpx.HTTPStatusError("unauth", request=MagicMock(), response=response)
        assert _is_retryable_error(exc) is False

    def test_value_error_not_retryable(self):
        assert _is_retryable_error(ValueError("bad input")) is False

    def test_runtime_error_not_retryable(self):
        assert _is_retryable_error(RuntimeError("unexpected")) is False

    def test_overloaded_name_retryable(self):
        class OverloadedError(Exception):
            pass
        assert _is_retryable_error(OverloadedError("api busy")) is True


# ── _invoke_with_retry ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_invoke_with_retry_succeeds_first_try():
    model = AsyncMock()
    model.ainvoke = AsyncMock(return_value="response")
    result = await _invoke_with_retry(model, ["msg"], max_api_retries=3)
    assert result == "response"
    assert model.ainvoke.await_count == 1


@pytest.mark.asyncio
async def test_invoke_with_retry_retries_on_timeout():
    model = AsyncMock()
    model.ainvoke = AsyncMock(
        side_effect=[httpx.ReadTimeout("timed out"), "ok"]
    )
    with patch("yt_agent.agents.base.asyncio.sleep", new_callable=AsyncMock):
        result = await _invoke_with_retry(model, ["msg"], max_api_retries=2)
    assert result == "ok"
    assert model.ainvoke.await_count == 2


@pytest.mark.asyncio
async def test_invoke_with_retry_raises_after_max_retries():
    model = AsyncMock()
    model.ainvoke = AsyncMock(
        side_effect=httpx.ReadTimeout("timed out"),
    )
    with (
        patch("yt_agent.agents.base.asyncio.sleep", new_callable=AsyncMock),
        pytest.raises(httpx.ReadTimeout),
    ):
        await _invoke_with_retry(model, ["msg"], max_api_retries=3)
    assert model.ainvoke.await_count == 3


@pytest.mark.asyncio
async def test_invoke_with_retry_no_retry_on_400():
    response = MagicMock()
    response.status_code = 400
    exc = httpx.HTTPStatusError("bad request", request=MagicMock(), response=response)
    model = AsyncMock()
    model.ainvoke = AsyncMock(side_effect=exc)
    with pytest.raises(httpx.HTTPStatusError):
        await _invoke_with_retry(model, ["msg"], max_api_retries=3)
    assert model.ainvoke.await_count == 1


@pytest.mark.asyncio
async def test_invoke_with_retry_retries_429():
    response = MagicMock()
    response.status_code = 429
    exc = httpx.HTTPStatusError("rate limited", request=MagicMock(), response=response)
    model = AsyncMock()
    model.ainvoke = AsyncMock(side_effect=[exc, "ok"])
    with patch("yt_agent.agents.base.asyncio.sleep", new_callable=AsyncMock):
        result = await _invoke_with_retry(model, ["msg"], max_api_retries=2)
    assert result == "ok"


# ── JSON parse retry in invoke_agent_with_tools ─────────────────────


@pytest.mark.asyncio
async def test_json_parse_retry_sends_error_feedback():
    """When JSON parsing fails, the agent re-prompts with the Pydantic error."""
    valid_json = (
        '{"keyword":"IA","volume":100,"competition":50,"overall":60,'
        '"verdict":"approved","alternatives":[],'
        '"golden_checklist":{"universal_angle":"X",'
        '"short_premise":"Y","persona_trigger":"Z"}}'
    )

    bad_response = MagicMock()
    bad_response.content = "Not valid JSON at all"
    bad_response.tool_calls = []

    good_response = MagicMock()
    good_response.content = valid_json
    good_response.tool_calls = []

    llm = AsyncMock()
    llm.bind_tools = MagicMock(return_value=llm)
    llm.ainvoke = AsyncMock(side_effect=[bad_response, good_response])

    from yt_agent.agents.base import invoke_agent_with_tools

    result = await invoke_agent_with_tools(
        system_prompt="test",
        user_message="test",
        tools=[],
        llm=llm,
        output_schema=ThemeValidation,
        max_retries=2,
        max_api_retries=1,
    )

    assert result.keyword == "IA"
    assert llm.ainvoke.await_count == 2

    # The second ainvoke call receives messages that include the feedback
    # The feedback HumanMessage is the last message added before retrying
    second_call_messages = llm.ainvoke.call_args_list[1][0][0]
    # Find the feedback message (HumanMessage with parse error)
    from langchain_core.messages import HumanMessage

    feedback_msgs = [
        m for m in second_call_messages
        if isinstance(m, HumanMessage) and "could not be parsed" in m.content
    ]
    assert len(feedback_msgs) == 1
    assert "ThemeValidation" in feedback_msgs[0].content
