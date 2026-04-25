"""Tests for the shared agent base utilities."""

from __future__ import annotations

import pytest

from yt_agent.agents.base import _parse_json_output, load_prompt
from yt_agent.state import ThemeValidation


def test_load_prompt_performance():
    content = load_prompt("performance.md")
    assert "Agente P" in content
    assert "Diagnóstico de Performance" in content


def test_load_prompt_competitive():
    content = load_prompt("competitive.md")
    assert "Agente 0" in content
    assert "Análise Competitiva" in content


def test_load_prompt_validation():
    content = load_prompt("validation.md")
    assert "Agente V" in content
    assert "Validação de Tema" in content


def test_load_prompt_metadata():
    content = load_prompt("metadata.md")
    assert "Agente Meta" in content
    assert "Metadados" in content


def test_load_prompt_scriptwriter():
    content = load_prompt("scriptwriter.md")
    assert "Agente Roteirista" in content
    assert "DNA NARRATIVO" in content


def test_load_prompt_qa():
    content = load_prompt("qa.md")
    assert "Agente QA" in content
    assert "35" in content


def test_load_prompt_repackaging():
    content = load_prompt("repackaging.md")
    assert "Agente R" in content
    assert "Repackaging" in content


def test_parse_json_output_clean():
    json_str = """{
        "keyword": "test",
        "volume": 100,
        "competition": 50,
        "overall": 60,
        "verdict": "approved",
        "alternatives": [],
        "golden_checklist": {
            "universal_angle": "Everyone cares",
            "short_premise": "AI helps all",
            "persona_trigger": "Curiosity"
        }
    }"""
    result = _parse_json_output(json_str, ThemeValidation)
    assert result.keyword == "test"
    assert result.verdict == "approved"


def test_parse_json_output_with_markdown_fences():
    text = """Here's the result:

```json
{
    "keyword": "test",
    "volume": 100,
    "competition": 50,
    "overall": 60,
    "verdict": "approved",
    "alternatives": [],
    "golden_checklist": {
        "universal_angle": "Everyone cares",
        "short_premise": "AI helps all",
        "persona_trigger": "Curiosity"
    }
}
```"""
    result = _parse_json_output(text, ThemeValidation)
    assert result.keyword == "test"


def test_parse_json_output_no_json_raises():
    with pytest.raises(ValueError, match="No JSON object found"):
        _parse_json_output("This has no JSON", ThemeValidation)


def test_parse_json_output_invalid_schema_raises():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        _parse_json_output('{"keyword": "test"}', ThemeValidation)
