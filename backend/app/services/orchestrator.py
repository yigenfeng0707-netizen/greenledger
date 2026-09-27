"""Pipeline orchestration: runs agent stages, assigns audit-grade IDs, persists state."""

from __future__ import annotations

import time
from typing import List

from ..agents import pipeline
from ..config import UPLOAD_DIR
from ..models.schemas import ActivityItem, EmissionResult, Project
from . import emission_factors as ef
from . import store


def _load_raw(pid: str, file_name: str) -> bytes:
    path = UPLOAD_DIR / pid / file_name
    if path.exists():
        return path.read_bytes()
    return b""


def extract_all(pid: str) -> Project:
    p = store.get_project(pid)
    if p is None:
        raise KeyError(pid)
    next_n = len(p.activities) + 1
    for doc in p.documents:
        t0 = time.perf_counter()
        raw = _load_raw(pid, doc.file_name) if doc.text is None else None
        result = pipeline.run_extract(p, doc, raw)
        for item in result.items:
            item.id = f"A{next_n}"
            next_n += 1
            item.source.file_name = doc.file_name
            p.activities.append(item)
        store.add_audit(p, "extract", f"{doc.file_name}: {len(result.items)} activity record(s) extracted", int((time.perf_counter() - t0) * 1000))
    store.save_project(p)
    return p


def update_activity(pid: str, item_id: str, status: str, quantity: float | None = None, unit: str | None = None, category: str | None = None) -> Project:
    p = store.get_project(pid)
    if p is None:
        raise KeyError(pid)
    item = next((i for i in p.activities if i.id == item_id), None)
    if item is None:
        raise KeyError(item_id)
    if quantity is not None:
        item.quantity = quantity
    if unit is not None:
        item.unit = unit
    if category is not None:
        item.category = category
    item.status = status
    store.add_audit(p, "review", f"{item_id} marked {status}" + (f" (qty {item.quantity} {item.unit})" if status == "edited" else ""))
    store.save_project(p)
    return p


def map_all(pid: str) -> Project:
    p = store.get_project(pid)
    if p is None:
        raise KeyError(pid)
    usable = [i for i in p.activities if i.status != "rejected"]
    t0 = time.perf_counter()
    mapping = pipeline.run_map(p, usable)
    emissions: List[EmissionResult] = []
    for row in mapping.results:
        factor = ef.get_factor(row.factor_id)
        if factor is None:
            continue
        item = next((i for i in usable if i.id == row.item_id), None)
        if item is None:
            continue
        emissions.append(
            EmissionResult(
                item_id=row.item_id,
                factor_id=factor["id"],
                factor_name=factor["name"],
                quantity_in_factor_unit=row.quantity_in_factor_unit,
                factor_value=factor["value"],
                factor_unit=factor["unit"],
                co2e_kg=round(row.quantity_in_factor_unit * factor["value"], 2),
                scope=row.scope if row.scope in (1, 2, 3) else factor["scope"],
                rationale=row.rationale,
            )
        )
    p.emissions = emissions
    store.add_audit(p, "map", f"{len(emissions)} record(s) mapped to emission factors", int((time.perf_counter() - t0) * 1000))
    store.save_project(p)
    return p


def gaps_all(pid: str) -> Project:
    p = store.get_project(pid)
    if p is None:
        raise KeyError(pid)
    usable = [i for i in p.activities if i.status != "rejected"]
    t0 = time.perf_counter()
    ga = pipeline.run_gaps(p, usable, p.emissions)
    p.gaps = ga.items
    store.add_audit(p, "gaps", f"{len(ga.items)} disclosure gap(s) identified", int((time.perf_counter() - t0) * 1000))
    store.save_project(p)
    return p


def draft_all(pid: str) -> Project:
    p = store.get_project(pid)
    if p is None:
        raise KeyError(pid)
    usable = [i for i in p.activities if i.status != "rejected"]
    t0 = time.perf_counter()
    p.report = pipeline.run_draft(p, usable, p.emissions, p.gaps)
    store.add_audit(p, "draft", f"Disclosure draft generated ({len(p.report.sections)} sections)", int((time.perf_counter() - t0) * 1000))
    store.save_project(p)
    return p


def ask(pid: str, question: str) -> dict:
    p = store.get_project(pid)
    if p is None:
        raise KeyError(pid)
    usable = [i for i in p.activities if i.status != "rejected"]
    t0 = time.perf_counter()
    resp = pipeline.run_qa(p, question, usable, p.emissions, p.gaps)
    valid = {i.id for i in usable}
    resp.citations = [c for c in resp.citations if c in valid]
    store.add_audit(p, "ask", f"Q&A: “{question[:60]}” ({len(resp.citations)} citation(s))", int((time.perf_counter() - t0) * 1000))
    store.save_project(p)
    return {"answer": resp.answer, "citations": resp.citations}


def totals(p: Project) -> dict:
    by_scope = {1: 0.0, 2: 0.0, 3: 0.0}
    for e in p.emissions:
        by_scope[e.scope] = by_scope.get(e.scope, 0.0) + e.co2e_kg
    return {
        "total_co2e_kg": round(sum(by_scope.values()), 2),
        "by_scope_kg": {f"scope_{s}": round(v, 2) for s, v in by_scope.items()},
    }
