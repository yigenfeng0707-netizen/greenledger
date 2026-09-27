"""Deterministic mock "agents" used when no Gemini key is configured.

They parse the bundled sample documents with simple heuristics so the full
pipeline (extract -> map -> gaps -> report -> ask) can be demoed offline with
plausible, stable results. Real Gemini calls replace these one-for-one.
"""

from __future__ import annotations

import csv
import io
import re
from typing import Any, Dict, List, Optional

from ..models.schemas import (
    ActivityItem,
    EmissionResult,
    ExtractionResult,
    GapAnalysis,
    GapItem,
    MappingResult,
    MappingResultRow,
    QAResponse,
    ReportDraft,
    ReportSection,
)
from . import emission_factors as ef

_MONTH = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[- ]?20\d\d"


def _period_from(text: str) -> Optional[str]:
    m = re.search(_MONTH, text)
    return m.group(0) if m else None


def mock_extract(file_name: str, text: str) -> ExtractionResult:
    items: List[ActivityItem] = []
    lower = text.lower()
    period = _period_from(text)

    def add(category: str, description: str, qty: float, unit: str, excerpt: str, scope_guess: int):
        items.append(
            ActivityItem(
                category=category,
                description=description,
                quantity=qty,
                unit=unit,
                period=period,
                scope_guess=scope_guess,
                confidence=0.9,
                source={"file_name": file_name, "excerpt": excerpt.strip()[:160]},
            )
        )

    # Flight itinerary CSV: date,route,from,to,passengers,distance_km,cabin
    if file_name.lower().endswith(".csv") and ("flight" in lower or "distance_km" in lower):
        rows = list(csv.DictReader(io.StringIO(text)))
        for r in rows:
            try:
                pax = float(r.get("passengers") or 0)
                dist = float(r.get("distance_km") or 0)
            except ValueError:
                continue
            excerpt = ",".join(f"{k}={v}" for k, v in r.items())
            add(
                "air_travel",
                f"Business flight {r.get('route') or (str(r.get('from')) + '-' + str(r.get('to')))}, {int(pax)} passenger(s), {int(dist)} km",
                pax * dist,
                "passenger-km",
                excerpt,
                3,
            )
        return ExtractionResult(items=items)

    # Line-based heuristics; each rule: (predicate, number regex, category, description, unit, scope)
    def number_before(line: str, tail: str) -> Optional[float]:
        m = re.search(r"([\d,\.]+)\s*" + tail, line.lower())
        if not m:
            return None
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            return None

    rules = [
        # electricity: skip meter-reading rows and rate lines (contain 'x' or 'reading')
        (lambda l: "kwh" in l and "reading" not in l and " x " not in l and "x 0" not in l,
         "kwh", "electricity", "Purchased grid electricity", "kWh", 2),
        (lambda l: "m3" in l and "gas" in l and "reading" not in l and "meter g" not in l,
         "m3", "natural_gas", "Natural gas (stationary combustion)", "m3", 1),
        (lambda l: "diesel" in l and "liter" in l and "week" not in l and "refill" not in l,
         "liters?", "diesel", "Diesel fuel consumed (delivery vans)", "liter", 1),
        (lambda l: "tonne" in l and "landfill" in l,
         "tonnes?", "waste", "Mixed general waste to landfill", "tonne", 3),
        (lambda l: "tonne" in l and "recycl" in l,
         "tonnes?", "waste", "Mixed recyclables sent for recycling", "tonne", 3),
        (lambda l: "km" in l and "car" in l and "/day" not in l and "average" not in l,
         "km", "road_passenger", "Employee commute by car", "km", 3),
        (lambda l: "hotel" in l and "night" in l,
         "nights?", "hotel", "Hotel stays (business travel)", "night", 3),
    ]
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        low = line.lower()
        for pred, tail, cat, desc, unit, scope in rules:
            if not pred(low):
                continue
            if len(re.findall(tail, low)) > 1:
                break  # e.g. meter rows carry two kWh readings — not a single consumption figure
            qty = number_before(line, tail)
            if qty is None or qty == 0:
                continue
            add(cat, desc, qty, unit, line, scope)
            break

    return ExtractionResult(items=items)


def mock_mapping(items: List[ActivityItem]) -> MappingResult:
    rows: List[MappingResultRow] = []
    for it in items:
        cands = ef.search_factors(it.category, it.description)
        f = cands[0]
        if it.unit == f["unit"]:
            qty = it.quantity
        elif it.unit == "litre" and f["unit"] == "liter":
            qty = it.quantity
        else:
            qty = it.quantity  # demo samples are authored in factor units
        rows.append(
            MappingResultRow(
                item_id=it.id,
                factor_id=f["id"],
                quantity_in_factor_unit=qty,
                scope=f["scope"],
                rationale=f"Matched factor '{f['name']}' for category {it.category}.",
            )
        )
    return MappingResult(results=rows)


_IFRS_S2_GAPS = [
    {
        "requirement": "IFRS S2 §29(a) - Cross-industry metric categories",
        "description": "No Scope 3 data for purchased goods & services, which usually dominates SME footprints.",
        "severity": "high",
        "suggestion": "Collect spend data and apply an EEIO (input-output) screening, then refine top suppliers.",
    },
    {
        "requirement": "IFRS S2 §29(b) - Targets",
        "description": "No emissions-reduction target disclosed (base year, target year, % reduction).",
        "severity": "high",
        "suggestion": "Set a near-term target (e.g. -30% Scope 1+2 by 2030 vs 2025 base year) with interim milestones.",
    },
    {
        "requirement": "IFRS S2 §28 - Methodology & consolidation approach",
        "description": "Consolidation approach (operational vs financial control) is not documented.",
        "severity": "medium",
        "suggestion": "State the approach in the methodology note; keep grid-factor vintage and sources per audit trail.",
    },
    {
        "requirement": "GHG Protocol Scope 2 Guidance - Dual reporting",
        "description": "Only location-based Scope 2 available; market-based figure requires supplier contracts.",
        "severity": "low",
        "suggestion": "Obtain residual-mix factors or renewable energy certificates (RECs) for market-based Scope 2.",
    },
]


def mock_gaps() -> GapAnalysis:
    return GapAnalysis(items=[GapItem(**g) for g in _IFRS_S2_GAPS])


def mock_report(emissions: List[EmissionResult], items: List[ActivityItem], gaps: List[GapItem]) -> ReportDraft:
    total_kg = sum(e.co2e_kg for e in emissions)
    by_scope: Dict[str, float] = {}
    for e in emissions:
        key = f"Scope {e.scope}"
        by_scope[key] = round(by_scope.get(key, 0.0) + e.co2e_kg / 1000.0, 3)

    def cite(item_id: str) -> str:
        return f"[{item_id}]"

    s1 = [e for e in emissions if e.scope == 1]
    s2 = [e for e in emissions if e.scope == 2]
    s3 = [e for e in emissions if e.scope == 3]

    def bullet(e: EmissionResult) -> str:
        it = next((i for i in items if i.id == e.item_id), None)
        period = f" ({it.period})" if it and it.period else ""
        return f"- {e.quantity_in_factor_unit:g} {e.factor_unit} x {e.factor_value} kgCO2e/{e.factor_unit} = **{e.co2e_kg:,.1f} kgCO2e** {cite(e.item_id)}{period}"

    sections = [
        ReportSection(
            heading="1. Organizational boundary & methodology",
            content=(
                "This inventory follows the GHG Protocol Corporate Standard. Activity data was collected from "
                "source documents (utility bills, fuel logs, travel records) and processed by the GreenLedger "
                "agentic pipeline; every figure carries a citation to its source document for audit purposes.\n\n"
                f"- Reporting period: as stated per source document\n- Consolidation approach: operational control *(to be confirmed)*\n"
                f"- Emission factors: bundled reference library (see sources) — {len(ef.all_factors())} factors available"
            ),
        ),
        ReportSection(
            heading="2. Scope 1 - Direct emissions",
            content=(
                "\n".join(bullet(e) for e in s1) if s1 else "- No Scope 1 activity data found in the uploaded documents."
            ),
        ),
        ReportSection(
            heading="3. Scope 2 - Purchased energy (location-based)",
            content=(
                "\n".join(bullet(e) for e in s2) if s2 else "- No Scope 2 activity data found in the uploaded documents."
            ),
        ),
        ReportSection(
            heading="4. Scope 3 - Value chain emissions (partial)",
            content=(
                "\n".join(bullet(e) for e in s3) if s3 else "- No Scope 3 activity data found in the uploaded documents."
            ),
        ),
        ReportSection(
            heading="5. Data gaps & improvement plan",
            content="\n".join(
                f"- **{g.requirement}**: {g.description} → {g.suggestion}" for g in gaps
            ),
        ),
    ]
    return ReportDraft(
        title="GHG Inventory Disclosure Draft (IFRS S2-aligned)",
        period="Draft for review",
        summary=(
            f"Total estimated footprint: **{total_kg / 1000.0:,.2f} tCO2e** across "
            f"{len(emissions)} quantified activity records. Scope split: "
            + ", ".join(f"{k}: {v:,.2f} tCO2e" for k, v in sorted(by_scope.items()))
            + ". All figures are traceable to cited source documents."
        ),
        sections=sections,
    )


def mock_qa(question: str, items: List[ActivityItem], emissions: List[EmissionResult], gaps: List[GapItem]) -> QAResponse:
    q = question.lower()
    used: List[str] = []

    def ids_for(scopes: List[int], categories: Optional[List[str]] = None) -> List[EmissionResult]:
        out = []
        for e in emissions:
            it = next((i for i in items if i.id == e.item_id), None)
            if e.scope in scopes and (categories is None or (it and it.category in categories)):
                out.append(e)
        return out

    def fmt(es: List[EmissionResult]) -> str:
        kg = sum(e.co2e_kg for e in es)
        return f"{kg / 1000.0:,.2f} tCO2e across {len(es)} record(s)"

    if any(k in q for k in ("scope 1", "direct")):
        es = ids_for([1])
        used = [e.item_id for e in es]
        ans = f"Scope 1 (direct emissions from combustion) totals {fmt(es)}." if es else "No Scope 1 records found."
    elif any(k in q for k in ("scope 2", "electricity", "power")):
        es = ids_for([2])
        used = [e.item_id for e in es]
        ans = f"Scope 2 (location-based, purchased electricity) totals {fmt(es)}." if es else "No Scope 2 records found."
    elif any(k in q for k in ("travel", "flight", "air")):
        es = ids_for([3], ["air_travel"])
        used = [e.item_id for e in es]
        ans = f"Business air travel totals {fmt(es)}." if es else "No air-travel records found."
    elif any(k in q for k in ("waste", "landfill")):
        es = ids_for([3], ["waste"])
        used = [e.item_id for e in es]
        ans = f"Waste-related Scope 3 emissions total {fmt(es)}." if es else "No waste records found."
    elif any(k in q for k in ("total", "footprint", "overall", "summary")):
        used = [e.item_id for e in emissions]
        ans = f"The total estimated footprint is {fmt(emissions)}. Scope breakdown: " + ", ".join(
            f"Scope {s}: {sum(e.co2e_kg for e in emissions if e.scope == s) / 1000.0:,.2f} tCO2e"
            for s in sorted({e.scope for e in emissions})
        ) + "."
    elif any(k in q for k in ("missing", "gap", "improve", "target")):
        used = []
        ans = "The main disclosure gaps are: " + " ".join(
            f"({g.requirement}: {g.suggestion})" for g in gaps
        )
    else:
        used = [e.item_id for e in emissions]
        ans = (
            f"I can answer from {len(emissions)} quantified records currently in the inventory. "
            "Ask about Scope 1/2/3, air travel, waste, or the total footprint; cited records are listed."
        )
    return QAResponse(answer=ans, citations=used)
