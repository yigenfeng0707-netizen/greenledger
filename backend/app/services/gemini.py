"""Thin Gemini client for structured JSON output.

All agents go through `generate_structured`; when no API key is configured the
callers fall back to the deterministic mock engine (see mock_ai.py) so the app
runs end-to-end offline.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Type, TypeVar, Union

from pydantic import BaseModel

from ..config import settings

T = TypeVar("T", bound=BaseModel)

_client = None  # lazy google.genai.Client

PartLike = Union[str, object]  # str | google.genai.types.Part


class GeminiUnavailable(Exception):
    pass


def _model_chain(model: Optional[str]) -> List[str]:
    """Primary model first, then fallbacks for overload/unavailable errors."""
    primary = model or settings.model_fast
    chain = [primary]
    for fb in ("gemini-3.7-flash", "gemini-3.5-flash", "gemini-3.1-flash-lite"):
        if fb != primary:
            chain.append(fb)
    return chain


def _get_client():
    global _client
    if _client is None:
        try:
            from google import genai
        except ImportError as e:  # pragma: no cover
            raise GeminiUnavailable("google-genai not installed") from e
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def generate_structured(
    contents: Sequence[PartLike],
    schema: Type[T],
    model: Optional[str] = None,
    system: Optional[str] = None,
    temperature: float = 0.2,
) -> T:
    if settings.use_mock:
        raise GeminiUnavailable("mock mode active")
    from google import genai as _genai
    from google.genai import types

    last_error: Exception | None = None
    for candidate in _model_chain(model):
        try:
            resp = _get_client().models.generate_content(
                model=candidate,
                contents=list(contents),
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=temperature,
                ),
            )
            parsed = getattr(resp, "parsed", None)
            if parsed is None:
                raise GeminiUnavailable(
                    f"empty model response: {resp.text[:200] if resp.text else 'n/a'}"
                )
            return parsed
        except GeminiUnavailable:
            raise
        except (_genai.errors.ServerError, _genai.errors.ClientError) as e:
            # 503 overload / 404 model retired -> try next model in the chain
            last_error = e
            continue
    raise GeminiUnavailable(f"all models in chain failed: {last_error}")


def pdf_part(data: bytes) -> PartLike:
    from google.genai import types

    return types.Part.from_bytes(data=data, mime_type="application/pdf")


def image_part(data: bytes, mime_type: str) -> PartLike:
    from google.genai import types

    return types.Part.from_bytes(data=data, mime_type=mime_type)
