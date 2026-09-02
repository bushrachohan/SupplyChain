"""
tests/test_explainer.py

Standalone tests for llm/explainer.py. These tests NEVER call the real
Groq API — they use a fake client (dependency injection via the `client`
param) so they're fast, free, and deterministic in CI.
"""

import pytest

from llm.explainer import (
    ExplainerError,
    _build_explanation_messages,
    explain_recommendation,
    summarize_text,
)


class _FakeMessage:
    def __init__(self, content):
        self.content = content


class _FakeChoice:
    def __init__(self, content):
        self.message = _FakeMessage(content)


class _FakeResponse:
    def __init__(self, content):
        self.choices = [_FakeChoice(content)] if content is not None else []


class _FakeChatCompletions:
    def __init__(self, content=None, raise_error=False):
        self._content = content
        self._raise_error = raise_error

    def create(self, **kwargs):
        if self._raise_error:
            raise RuntimeError("simulated network failure")
        return _FakeResponse(self._content)


class _FakeChat:
    def __init__(self, content=None, raise_error=False):
        self.completions = _FakeChatCompletions(content, raise_error)


class FakeGroqClient:
    """Stands in for groq.Groq without any network access."""

    def __init__(self, content=None, raise_error=False):
        self.chat = _FakeChat(content, raise_error)


# --- _build_explanation_messages (pure function, no API involved) ---

def test_build_explanation_messages_includes_all_given_numbers():
    messages = _build_explanation_messages(
        situation="SKU-001 stockout risk",
        predictions={"days_of_supply": 2.94},
        policies_retrieved=[{"text": "14 days safety stock"}],
        options_considered=[{"option": "A", "cost": 450}],
        recommended_option={"option": "A", "cost": 450},
    )
    assert messages[0]["role"] == "system"
    assert "never invent" in messages[0]["content"].lower()
    user_content = messages[1]["content"]
    assert "2.94" in user_content
    assert "14 days safety stock" in user_content
    assert "450" in user_content


# --- explain_recommendation: validation ---

def test_explain_recommendation_rejects_empty_situation():
    with pytest.raises(ValueError):
        explain_recommendation(
            situation="",
            predictions={},
            policies_retrieved=[],
            options_considered=[],
            recommended_option={"option": "A"},
        )


def test_explain_recommendation_rejects_empty_recommended_option():
    with pytest.raises(ValueError):
        explain_recommendation(
            situation="Some situation",
            predictions={},
            policies_retrieved=[],
            options_considered=[],
            recommended_option={},
        )


# --- explain_recommendation: success path with fake client ---

def test_explain_recommendation_returns_stripped_content():
    fake_client = FakeGroqClient(content="  Recommendation explained.  ")
    result = explain_recommendation(
        situation="SKU-001 stockout risk",
        predictions={"days_of_supply": 2.94},
        policies_retrieved=[{"text": "14 days safety stock"}],
        options_considered=[{"option": "A", "cost": 450}],
        recommended_option={"option": "A", "cost": 450},
        client=fake_client,
    )
    assert result == "Recommendation explained."


# --- explain_recommendation: API failure handling ---

def test_explain_recommendation_wraps_api_exception():
    fake_client = FakeGroqClient(raise_error=True)
    with pytest.raises(ExplainerError):
        explain_recommendation(
            situation="SKU-001 stockout risk",
            predictions={},
            policies_retrieved=[],
            options_considered=[],
            recommended_option={"option": "A"},
            client=fake_client,
        )


def test_explain_recommendation_raises_on_empty_content():
    fake_client = FakeGroqClient(content=None)
    with pytest.raises(ExplainerError):
        explain_recommendation(
            situation="SKU-001 stockout risk",
            predictions={},
            policies_retrieved=[],
            options_considered=[],
            recommended_option={"option": "A"},
            client=fake_client,
        )


# --- summarize_text ---

def test_summarize_text_rejects_empty_text():
    with pytest.raises(ValueError):
        summarize_text("   ")


def test_summarize_text_returns_stripped_content():
    fake_client = FakeGroqClient(content="  A short summary.  ")
    result = summarize_text("Some long policy text.", client=fake_client)
    assert result == "A short summary."


def test_summarize_text_wraps_api_exception():
    fake_client = FakeGroqClient(raise_error=True)
    with pytest.raises(ExplainerError):
        summarize_text("Some text", client=fake_client)