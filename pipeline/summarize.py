"""Summarize a video transcript into structured sections.

Supports two backends, selected by the ``backend`` argument:
- ``"ollama"``     — local Ollama server (default model: qwen3.5:latest)
- ``"anthropic"``  — Anthropic API (requires ANTHROPIC_API_KEY env var)
"""
from __future__ import annotations

import json
import os
import re
from typing import Literal, TypedDict

import httpx


class DeepDive(TypedDict):
    core_concepts: str
    equations: list[str]
    examples: str


class Summary(TypedDict):
    abstract: str
    key_insights: list[str]
    deep_dive: DeepDive


_SYSTEM = """\
You are an expert science communicator. Given a raw YouTube video transcript, \
produce a structured JSON summary with exactly these keys:

{
  "abstract": "<1-2 paragraph overview of what the video covers>",
  "key_insights": ["<insight 1>", ..., "<insight N>"],  // 4-8 items
  "deep_dive": {
    "core_concepts": "<multi-paragraph explanation of the central ideas>",
    "equations": ["<LaTeX source, no delimiters>", ...],  // omit if none
    "examples": "<concrete examples and applications discussed>"
  }
}

Rules:
- Return ONLY valid JSON, no markdown fences.
- key_insights: 4–8 concise bullet strings (no leading dash or bullet char).
- equations: raw LaTeX only (e.g. "E = mc^2"), no $$ wrappers.
- If the video has no equations, return an empty list for "equations".
- Write in clear, engaging prose appropriate for an educated non-specialist.
"""


_OLLAMA_URL = "http://localhost:11434/api/chat"
_OLLAMA_MODEL = "qwen3.5:latest"
_ANTHROPIC_MODEL = "claude-sonnet-4-6"

_OLLAMA_SCHEMA = {
    "type": "object",
    "properties": {
        "abstract": {"type": "string"},
        "key_insights": {"type": "array", "items": {"type": "string"}},
        "deep_dive": {
            "type": "object",
            "properties": {
                "core_concepts": {"type": "string"},
                "equations": {"type": "array", "items": {"type": "string"}},
                "examples": {"type": "string"},
            },
            "required": ["core_concepts", "equations", "examples"],
        },
    },
    "required": ["abstract", "key_insights", "deep_dive"],
}

Backend = Literal["ollama", "anthropic"]


def _parse(raw: str) -> Summary:
    """Strip thinking tags / fences and parse JSON into a Summary."""
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
    if not raw:
        raise ValueError("Model returned empty content after stripping think/fence blocks")
    data = json.loads(raw)
    deep_dive_raw = data.get("deep_dive", {})
    # Model may return deep_dive as a plain string instead of a nested object
    if isinstance(deep_dive_raw, str):
        deep_dive_raw = {"core_concepts": deep_dive_raw, "equations": [], "examples": ""}
    deep_dive = deep_dive_raw
    return Summary(
        abstract=str(data.get("abstract", "")),
        key_insights=list(data.get("key_insights", [])),
        deep_dive=DeepDive(
            core_concepts=str(deep_dive.get("core_concepts", "")),
            equations=list(deep_dive.get("equations", [])),
            examples=str(deep_dive.get("examples", "")),
        ),
    )


def _summarize_ollama(transcript: str, title: str, model: str = _OLLAMA_MODEL, url: str = _OLLAMA_URL) -> Summary:
    response = httpx.post(
        url,
        json={
            "model": model,
            "stream": False,
            "think": False,
            "format": _OLLAMA_SCHEMA,  # enforce exact output structure
            "messages": [
                {"role": "system", "content": _SYSTEM},
                {
                    "role": "user",
                    "content": (
                        f"Video title: {title}\n\n"
                        f"Transcript:\n{transcript[:40000]}\n\n"
                        "Return ONLY a JSON object with keys: abstract, key_insights, deep_dive. "
                        "No prose, no markdown, no explanation — just the JSON."
                    ),
                },
            ],
        },
        timeout=300,
    )
    response.raise_for_status()
    content = response.json()["message"]["content"]
    return _parse(content)


def _summarize_anthropic(transcript: str, title: str, model: str = _ANTHROPIC_MODEL) -> Summary:
    import anthropic  # imported lazily — only needed when this backend is active

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model=model,
        max_tokens=2048,
        system=_SYSTEM,
        messages=[{"role": "user", "content": f"Video title: {title}\n\nTranscript:\n{transcript[:40000]}"}],
    )
    return _parse(message.content[0].text)


def summarize(
    transcript: str,
    title: str,
    backend: Backend = "ollama",
    *,
    ollama_model: str = _OLLAMA_MODEL,
    anthropic_model: str = _ANTHROPIC_MODEL,
) -> Summary:
    if backend == "anthropic":
        return _summarize_anthropic(transcript, title, model=anthropic_model)
    return _summarize_ollama(transcript, title, model=ollama_model)
