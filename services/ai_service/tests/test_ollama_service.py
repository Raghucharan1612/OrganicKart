"""
Regression tests for OllamaService.

Root cause fixed: gpt-oss:20b has "thinking" capability. When num_predict is
exhausted by reasoning tokens, Ollama returns response="" causing:
  "model output must contain either output text or tool calls, these cannot both be empty"

Fix applied:
  - think=False added to every /api/generate payload (suppresses reasoning tokens)
  - Empty response + thinking field is detected, logged, and raised as HTTP 502
  - OLLAMA_NUM_PREDICT bumped from 250 to 512 for safer headroom
"""

import asyncio
import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException

from app.services.ollama_service import OllamaService
from app.config import settings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_response(body: dict, status_code: int = 200) -> MagicMock:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.json.return_value = body
    return resp


def _run(coro):
    """Run a coroutine synchronously - compatible with Python 3.13+."""
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# think=False is sent in the payload
# ---------------------------------------------------------------------------

def test_ollama_sends_think_false_in_payload(monkeypatch):
    """think=False must appear in every /api/generate request."""
    captured: dict = {}

    async def mock_post(url, json, **kwargs):
        captured.update(json)
        return _make_response({"response": "2", "done": True})

    monkeypatch.setattr(settings, "MOCK_LLM", False)
    monkeypatch.setattr(settings, "OLLAMA_THINK", False)
    service = OllamaService()
    with patch.object(httpx.AsyncClient, "post", new=AsyncMock(side_effect=mock_post)):
        _run(service.generate_response("What is 1+1?"))

    assert "think" in captured, "think key must be in Ollama payload"
    assert captured["think"] is False


def test_ollama_think_flag_respects_config(monkeypatch):
    """OLLAMA_THINK=True is forwarded as-is."""
    captured: dict = {}

    async def mock_post(url, json, **kwargs):
        captured.update(json)
        return _make_response({"response": "ok", "done": True})

    monkeypatch.setattr(settings, "MOCK_LLM", False)
    monkeypatch.setattr(settings, "OLLAMA_THINK", True)
    service = OllamaService()
    with patch.object(httpx.AsyncClient, "post", new=AsyncMock(side_effect=mock_post)):
        _run(service.generate_response("Hello"))

    assert captured["think"] is True


# ---------------------------------------------------------------------------
# Empty response with thinking field (root cause)
# ---------------------------------------------------------------------------

def test_ollama_raises_502_when_response_empty_and_thinking_present(monkeypatch):
    """
    Regression for the 'model output must contain either output text or tool calls'
    error. When response="" but thinking is non-empty, OllamaService must raise 502.
    """
    monkeypatch.setattr(settings, "MOCK_LLM", False)
    monkeypatch.setattr(settings, "OLLAMA_THINK", False)
    body = {
        "response": "",
        "thinking": "We have a user question: What is 1+1? The answer is 2.",
        "done": True,
        "done_reason": "length",
    }
    service = OllamaService()
    with patch.object(httpx.AsyncClient, "post", new=AsyncMock(return_value=_make_response(body))):
        with pytest.raises(HTTPException) as exc_info:
            _run(service.generate_response("What is 1+1?"))

    assert exc_info.value.status_code == 502
    assert "empty response" in exc_info.value.detail.lower()


def test_ollama_raises_502_when_response_whitespace_only(monkeypatch):
    """Whitespace-only response is treated as empty."""
    monkeypatch.setattr(settings, "MOCK_LLM", False)
    monkeypatch.setattr(settings, "OLLAMA_THINK", False)
    service = OllamaService()
    with patch.object(
        httpx.AsyncClient, "post",
        new=AsyncMock(return_value=_make_response({"response": "   \n  ", "done": True}))
    ):
        with pytest.raises(HTTPException) as exc_info:
            _run(service.generate_response("Hello"))

    assert exc_info.value.status_code == 502


def test_ollama_raises_502_when_response_key_missing(monkeypatch):
    """Missing response key raises HTTP 502."""
    monkeypatch.setattr(settings, "MOCK_LLM", False)
    monkeypatch.setattr(settings, "OLLAMA_THINK", False)
    service = OllamaService()
    with patch.object(
        httpx.AsyncClient, "post",
        new=AsyncMock(return_value=_make_response({"done": True}))
    ):
        with pytest.raises(HTTPException) as exc_info:
            _run(service.generate_response("Hello"))

    assert exc_info.value.status_code == 502


# ---------------------------------------------------------------------------
# Ollama error body (HTTP 200 but error key)
# ---------------------------------------------------------------------------

def test_ollama_raises_502_on_error_body(monkeypatch):
    """
    Ollama HTTP 200 response with error key (no response key) raises 502.
    This is the exact payload produced by the reported error.
    """
    monkeypatch.setattr(settings, "MOCK_LLM", False)
    monkeypatch.setattr(settings, "OLLAMA_THINK", False)
    error_body = {
        "error": (
            "model output error: model output must contain either output text or tool calls, "
            "these cannot both be empty, please try again"
        )
    }
    service = OllamaService()
    with patch.object(
        httpx.AsyncClient, "post", new=AsyncMock(return_value=_make_response(error_body))
    ):
        with pytest.raises(HTTPException) as exc_info:
            _run(service.generate_response("What is 1+1?"))

    assert exc_info.value.status_code == 502


# ---------------------------------------------------------------------------
# Normal success path
# ---------------------------------------------------------------------------

def test_ollama_returns_response_text_on_success(monkeypatch):
    """Normal response text is returned unchanged (modulo strip)."""
    monkeypatch.setattr(settings, "MOCK_LLM", False)
    monkeypatch.setattr(settings, "OLLAMA_THINK", False)
    body = {"response": "OrganicKart delivers fresh organic produce.", "done": True}
    service = OllamaService()
    with patch.object(httpx.AsyncClient, "post", new=AsyncMock(return_value=_make_response(body))):
        result = _run(service.generate_response("What does OrganicKart offer?"))

    assert result == "OrganicKart delivers fresh organic produce."


def test_ollama_strips_whitespace_from_response(monkeypatch):
    monkeypatch.setattr(settings, "MOCK_LLM", False)
    monkeypatch.setattr(settings, "OLLAMA_THINK", False)
    service = OllamaService()
    with patch.object(
        httpx.AsyncClient, "post",
        new=AsyncMock(return_value=_make_response({"response": "  Hello!  ", "done": True}))
    ):
        result = _run(service.generate_response("Hi"))

    assert result == "Hello!"


def test_ollama_num_predict_uses_config(monkeypatch):
    """num_predict reflects OLLAMA_NUM_PREDICT (now 512 by default)."""
    monkeypatch.setattr(settings, "MOCK_LLM", False)
    monkeypatch.setattr(settings, "OLLAMA_NUM_PREDICT", 512)
    captured: dict = {}

    async def mock_post(url, json, **kwargs):
        captured.update(json)
        return _make_response({"response": "ok", "done": True})

    service = OllamaService()
    with patch.object(httpx.AsyncClient, "post", new=AsyncMock(side_effect=mock_post)):
        _run(service.generate_response("Hello"))

    assert captured["options"]["num_predict"] == 512


# ---------------------------------------------------------------------------
# Ollama HTTP error codes
# ---------------------------------------------------------------------------

def test_ollama_raises_502_on_http_400(monkeypatch):
    monkeypatch.setattr(settings, "MOCK_LLM", False)
    monkeypatch.setattr(settings, "OLLAMA_THINK", False)
    service = OllamaService()
    with patch.object(
        httpx.AsyncClient, "post",
        new=AsyncMock(return_value=_make_response({}, status_code=400))
    ):
        with pytest.raises(HTTPException) as exc_info:
            _run(service.generate_response("Hello"))
    assert exc_info.value.status_code == 502


def test_ollama_raises_502_on_model_not_found(monkeypatch):
    monkeypatch.setattr(settings, "MOCK_LLM", False)
    monkeypatch.setattr(settings, "OLLAMA_THINK", False)
    service = OllamaService()
    with patch.object(
        httpx.AsyncClient, "post",
        new=AsyncMock(return_value=_make_response({}, status_code=404))
    ):
        with pytest.raises(HTTPException) as exc_info:
            _run(service.generate_response("Hello"))
    assert exc_info.value.status_code == 502
    assert "ollama pull" in exc_info.value.detail


def test_ollama_raises_503_on_connect_error(monkeypatch):
    monkeypatch.setattr(settings, "MOCK_LLM", False)
    monkeypatch.setattr(settings, "OLLAMA_THINK", False)
    service = OllamaService()
    with patch.object(
        httpx.AsyncClient, "post",
        new=AsyncMock(side_effect=httpx.ConnectError("refused"))
    ):
        with pytest.raises(HTTPException) as exc_info:
            _run(service.generate_response("Hello"))
    assert exc_info.value.status_code == 503


def test_ollama_raises_504_on_timeout(monkeypatch):
    monkeypatch.setattr(settings, "MOCK_LLM", False)
    monkeypatch.setattr(settings, "OLLAMA_THINK", False)
    service = OllamaService()
    with patch.object(
        httpx.AsyncClient, "post",
        new=AsyncMock(side_effect=httpx.TimeoutException("timed out"))
    ):
        with pytest.raises(HTTPException) as exc_info:
            _run(service.generate_response("Hello"))
    assert exc_info.value.status_code == 504


def test_ollama_raises_502_on_generic_http_failure(monkeypatch):
    """Generic httpx.HTTPError raises HTTP 502 Bad Gateway."""
    monkeypatch.setattr(settings, "MOCK_LLM", False)
    monkeypatch.setattr(settings, "OLLAMA_THINK", False)
    service = OllamaService()
    with patch.object(
        httpx.AsyncClient, "post",
        new=AsyncMock(side_effect=httpx.RemoteProtocolError("connection closed prematurely"))
    ):
        with pytest.raises(HTTPException) as exc_info:
            _run(service.generate_response("Hello"))
    assert exc_info.value.status_code == 502
    assert "Failed to communicate with local Ollama LLM provider" in exc_info.value.detail
