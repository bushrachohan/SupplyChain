"""
llm/explainer.py

Groq API wrapper for the "explains only, never computes" layer of the
system (per Section 1, The LLM Grounding Constraint).

This module NEVER lets the LLM invent, calculate, or modify a numeric
value. It only accepts already-computed structured data (predictions,
retrieved policies, options considered, the recommended option — all
produced by core/*.py, ml/*.py, and core/rag.py) and asks Groq to narrate
and justify it in plain English. The system prompt explicitly instructs
the model not to introduce new numbers.

This module does not decide *which* option is recommended — that's
code-assembled (per agent/orchestrator.py design, Section 3, step 5). It
only explains a decision that has already been made.
"""

import os
from typing import Any, Optional

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

DEFAULT_MODEL = "openai/gpt-oss-120b"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 400

NO_INVENTION_SYSTEM_PROMPT = (
    "You are an explanation and narration assistant for a supply-chain "
    "decision support system. You NEVER invent, calculate, guess, or modify "
    "any numeric value. You only explain, summarize, and justify a decision "
    "using EXACTLY the numbers, facts, and policy text given to you in the "
    "user message. If a number is not provided to you, do not state a "
    "number for it — describe it qualitatively instead. Do not perform "
    "arithmetic. Do not round, estimate, or infer missing figures."
)


class ExplainerError(Exception):
    """Raised when the Groq API call fails or returns an unusable response."""


def get_groq_client(api_key: Optional[str] = None) -> Groq:
    """
    Build a Groq client from an explicit key or the GROQ_API_KEY env var.

    Raises:
        ValueError: if no API key is available anywhere.
    """
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to .env (see progress.md Section 6) "
            "or pass api_key explicitly."
        )
    return Groq(api_key=key)


def _build_explanation_messages(
    situation: str,
    predictions: dict[str, Any],
    policies_retrieved: list[dict[str, Any]],
    options_considered: list[dict[str, Any]],
    recommended_option: dict[str, Any],
) -> list[dict[str, str]]:
    """
    Build the chat messages for explain_recommendation. Kept as a separate,
    testable function so prompt construction can be verified without any
    API call.
    """
    user_prompt = f"""Situation:
{situation}

Model predictions / risk scores (already computed by code — do not alter):
{predictions}

Policies retrieved (must be respected — do not alter):
{policies_retrieved}

Options considered (already computed by code):
{options_considered}

Recommended option (already selected by code, not by you):
{recommended_option}

Write a clear, plain-English explanation (3-6 sentences) of why this option
was recommended. Reference the specific numbers and policies above exactly
as given. Do not introduce any new numeric values. Do not recommend a
different option than the one given."""

    return [
        {"role": "system", "content": NO_INVENTION_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def explain_recommendation(
    situation: str,
    predictions: dict[str, Any],
    policies_retrieved: list[dict[str, Any]],
    options_considered: list[dict[str, Any]],
    recommended_option: dict[str, Any],
    model: str = DEFAULT_MODEL,
    client: Optional[Groq] = None,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> str:
    """
    Ask Groq to narrate/justify an already-computed recommendation.

    Args:
        situation: plain-language description of what's being decided.
        predictions: code-computed numbers (e.g. forecast, risk scores).
        policies_retrieved: output of core.rag.retrieve_policies().
        options_considered: code-assembled options table.
        recommended_option: the option code selected as the recommendation.
        client: optional pre-built Groq client (mainly for testing /
            dependency injection). If omitted, one is built from
            GROQ_API_KEY.

    Returns:
        The narration text, stripped of leading/trailing whitespace.

    Raises:
        ValueError: if required inputs are missing/empty, or no API key
            is available.
        ExplainerError: if the Groq API call fails or returns no content.
    """
    if not situation or not situation.strip():
        raise ValueError("situation must not be empty")
    if not recommended_option:
        raise ValueError("recommended_option must not be empty")

    if client is None:
        client = get_groq_client()

    messages = _build_explanation_messages(
        situation, predictions, policies_retrieved, options_considered, recommended_option
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except Exception as e:
        raise ExplainerError(f"Groq API call failed: {e}") from e

    if not response.choices or not response.choices[0].message.content:
        raise ExplainerError("Groq API returned no content")

    return response.choices[0].message.content.strip()


def summarize_text(
    text: str,
    model: str = DEFAULT_MODEL,
    client: Optional[Groq] = None,
    max_tokens: int = 200,
) -> str:
    """
    General-purpose summarization helper (e.g. condensing a long policy
    document or a decision trace for display). Still narration-only —
    no numeric computation is expected or permitted here either.

    Raises:
        ValueError: if text is empty.
        ExplainerError: if the Groq API call fails or returns no content.
    """
    if not text or not text.strip():
        raise ValueError("text must not be empty")

    if client is None:
        client = get_groq_client()

    messages = [
        {
            "role": "system",
            "content": (
                "Summarize the following text in 2-3 plain-English sentences. "
                "Do not add any numbers, facts, or claims not present in the "
                "original text."
            ),
        },
        {"role": "user", "content": text},
    ]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=max_tokens,
        )
    except Exception as e:
        raise ExplainerError(f"Groq API call failed: {e}") from e

    if not response.choices or not response.choices[0].message.content:
        raise ExplainerError("Groq API returned no content")

    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    # Manual smoke test — requires a real GROQ_API_KEY in .env and network
    # access. Mirrors what `uv run python llm/explainer.py` should show you.
    sample_explanation = explain_recommendation(
        situation="SKU-001 is projected to stock out within 3 days.",
        predictions={"days_of_supply": 2.94, "risk_level": "STOCKOUT_RISK"},
        policies_retrieved=[
            {
                "section_title": "1. Safety Stock Buffer Requirements",
                "text": "Tier-1 SKUs must maintain a minimum of 14 days safety stock.",
            }
        ],
        options_considered=[
            {"option": "Emergency reallocation from regional warehouse", "cost": 450},
            {"option": "Expedited purchase order", "cost": 1200},
        ],
        recommended_option={
            "option": "Emergency reallocation from regional warehouse",
            "cost": 450,
        },
    )
    print(sample_explanation)
