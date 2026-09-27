"""Deterministic search over the bundled emission-factor library.

The mapping agent receives these candidates and must pick one; keeping search
deterministic (instead of letting the model invent factors) is what makes the
inventory auditable.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from ..config import BACKEND_DIR

_FACTORS: Optional[Dict[str, Any]] = None


def _load() -> Dict[str, Any]:
    global _FACTORS
    if _FACTORS is None:
        path = BACKEND_DIR / "app" / "data" / "emission_factors.json"
        with open(path, "r", encoding="utf-8") as f:
            _FACTORS = json.load(f)
    return _FACTORS


def all_factors() -> List[Dict[str, Any]]:
    return _load()["factors"]


def meta() -> Dict[str, Any]:
    return _load()["meta"]


def get_factor(factor_id: str) -> Optional[Dict[str, Any]]:
    for f in all_factors():
        if f["id"] == factor_id:
            return f
    return None


def search_factors(category: Optional[str], description: str, limit: int = 6) -> List[Dict[str, Any]]:
    text = f"{category or ''} {description}".lower()
    scored: List[tuple[float, Dict[str, Any]]] = []
    for f in all_factors():
        score = 0.0
        if category and category.lower() == f["category"].lower():
            score += 5.0
        if f["category"].lower() in text:
            score += 3.0
        for kw in f.get("keywords", []):
            if kw.lower() in text:
                score += 2.0
        if score > 0:
            scored.append((score, f))
    scored.sort(key=lambda x: -x[0])
    results = [f for _, f in scored[:limit]]
    # Never return empty: the agent needs options to reason about.
    return results or all_factors()[:limit]
