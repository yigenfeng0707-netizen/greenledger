"""Agent stage implementations: Gemini with structured output, mock fallback.

Each stage has a strict system prompt; extraction and mapping always operate
against deterministic inputs (document bytes / curated factor library) so the
resulting inventory is auditable end-to-end.
"""

from __future__ import annotations

import json
from typing import Dict, List, Optional

from ..config import settings
from ..models.schemas import (
    ActivityItem,
    Document,
    EmissionResult,
    ExtractionResult,
    GapAnalysis,
    GapItem,
    MappingResult,
    MappingResultRow,
    Project,
    QAResponse,
    ReportDraft,
)
from ..services import emission_factors as ef
from ..services import gemini, mock_ai

CATEGORIES = [
    "electricity", "natural_gas", "diesel", "gasoline", "lpg", "air_travel",
    "rail", "road_passenger", "freight", "waste", "paper", "water", "hotel",
    "refrigerant", "commute", "other",
]


def _contents_for_document(doc: Document, raw: Optional[bytes] = None) -> List[object]:
    if doc.text is not None:
        return [f"SOURCE DOCUMENT: {doc.file_name}\n\n{doc.text}"]
    if doc.mime_type == "application/pdf" and raw is not None:
        return [f"SOURCE DOCUMENT: {doc.file_name}\n\n", gemini.pdf_part(raw)]
    if doc.mime_type.startswith("image/") and raw is not None:
        return [f"SOURCE DOCUMENT: {doc.file_name}\n\n", gemini.image_part(raw, doc.mime_type)]
    return [f"SOURCE DOCUMENT: {doc.file_name} (unreadable content provided)"]


EXTRACT_SYSTEM = f"""You are the Ingestion Agent of an auditable GHG-inventory pipeline.
Extract every quantifiable activity datum relevant to a corporate carbon inventory from the source document.
Rules:
- Only report quantities explicitly present in the document; never estimate.
- category must be one of: {", ".join(CATEGORIES)}.
- quantity is numeric, unit exactly as stated (normalize litre->liter). For flights, quantity = passengers x distance_km in unit "passenger-km".
- excerpt: verbatim quote (<=40 words) supporting the number.
- period: reporting period if stated (e.g. "June 2025", "Q2 2025").
- scope_guess: 1 (direct combustion/fugitive), 2 (purchased electricity/steam), 3 (everything else). Null if unsure.
- confidence: 0..1 based on clarity of the source.
Return JSON: {{"items": [...]}}. Empty list if nothing relevant.
"""


def run_extract(p: Project, doc: Document, raw: Optional[bytes]) -> ExtractionResult:
    if settings.use_mock:
        return mock_ai.mock_extract(doc.file_name, doc.text or "")
    contents = _contents_for_document(doc, raw)
    return gemini.generate_structured(
        contents,
        ExtractionResult,
        model=settings.model_extract,
        system=EXTRACT_SYSTEM,
    )


MAP_SYSTEM = """You are the Mapping Agent of an auditable GHG-inventory pipeline.
For each activity item you receive a curated candidate list of emission factors (id, name, unit, scope, source).
Pick exactly one candidate per item — never invent factors. Determine quantity_in_factor_unit by converting the
stated quantity into the factor's unit when needed. Assign the scope from the factor. Give a <=25-word rationale.
Return JSON: {"results": [{"item_id", "factor_id", "quantity_in_factor_unit", "scope", "rationale"}]}.
"""


def run_map(p: Project, items: List[ActivityItem]) -> MappingResult:
    if settings.use_mock:
        return mock_ai.mock_mapping(items)
    rows = []
    for it in items:
        cands = ef.search_factors(it.category, it.description)
        payload = {
            "item": {
                "id": it.id, "category": it.category, "description": it.description,
                "quantity": it.quantity, "unit": it.unit, "period": it.period,
            },
            "candidate_factors": [
                {"id": c["id"], "name": c["name"], "value": c["value"], "unit": c["unit"],
                 "scope": c["scope"], "source": c["source"]}
                for c in cands
            ],
        }
        rows.append(json.dumps(payload))
    contents = ["Match each activity item to one candidate emission factor.\n"] + [
        f"\nITEM {i + 1}:\n{r}" for i, r in enumerate(rows)
    ]
    result = gemini.generate_structured(
        contents,
        MappingResult,
        model=settings.model_fast,
        system=MAP_SYSTEM,
    )
    # Drop any rows the model hallucinated or pointed at unknown factors.
    valid_ids = {it.id for it in items}
    result.results = [
        r for r in result.results if r.item_id in valid_ids and ef.get_factor(r.factor_id) is not None
    ]
    return result


GAP_SYSTEM = """You are the Gap Analysis Agent for a climate-disclosure pipeline.
Given the extracted activity records and computed emissions, list what is missing for an IFRS S2-aligned
(Industry-based metrics optional), GHG Protocol-compliant disclosure. Cover at most 6 gaps, each with:
requirement (e.g. "IFRS S2 §29(a) - Metrics"), description of what is missing, severity high|medium|low,
and one concrete suggestion.
Return JSON: {"items": [{"requirement", "description", "severity", "suggestion"}]}.
"""


def run_gaps(p: Project, items: List[ActivityItem], emissions: List[EmissionResult]) -> GapAnalysis:
    if settings.use_mock:
        return mock_ai.mock_gaps()
    facts = {
        "activity_categories_present": sorted({i.category for i in items}),
        "scopes_present": sorted({e.scope for e in emissions}),
        "n_records": len(items),
        "documents": [d.file_name for d in p.documents],
    }
    return gemini.generate_structured(
        [f"Project facts:\n{json.dumps(facts, indent=1)}\n\nIdentify disclosure gaps."],
        GapAnalysis,
        model=settings.model_fast,
        system=GAP_SYSTEM,
    )


DRAFT_SYSTEM = """You are the Drafting Agent for a climate-disclosure pipeline.
Write the disclosure draft from the verified data you are given. Rules:
- Markdown content per section; concise, audit-appropriate tone.
- Cite every number inline with the activity record id in square brackets, e.g. [A3]. Never state a number
  that is not present in the provided data.
- Sections: 1. Organizational boundary & methodology; 2. Scope 1 - Direct emissions; 3. Scope 2 - Purchased
  energy (location-based); 4. Scope 3 - Value chain emissions (partial); 5. Data gaps & improvement plan.
Return JSON: {"title", "period", "summary", "sections": [{"heading", "content"}]}.
"""


def run_draft(p: Project, items: List[ActivityItem], emissions: List[EmissionResult], gaps: GapAnalysis) -> ReportDraft:
    total_kg = sum(e.co2e_kg for e in emissions)
    by_scope: Dict[str, float] = {}
    for e in emissions:
        by_scope[f"scope_{e.scope}"] = round(by_scope.get(f"scope_{e.scope}", 0.0) + e.co2e_kg / 1000.0, 3)

    if settings.use_mock:
        return mock_ai.mock_report(emissions, items, gaps)

    payload = {
        "activity_records": [
            {"id": i.id, "category": i.category, "description": i.description, "quantity": i.quantity,
             "unit": i.unit, "period": i.period, "source_file": i.source.file_name}
            for i in items
        ],
        "computed_emissions": [
            {"item_id": e.item_id, "factor_name": e.factor_name,
             "quantity_in_factor_unit": e.quantity_in_factor_unit, "factor_unit": e.factor_unit,
             "co2e_kg": e.co2e_kg, "scope": e.scope}
            for e in emissions
        ],
        "totals": {"total_tco2e": round(total_kg / 1000.0, 3), **by_scope},
        "gaps": [g.model_dump() for g in gaps.items],
    }
    return gemini.generate_structured(
        [f"Verified data:\n{json.dumps(payload, indent=1)}\n\nWrite the disclosure draft."],
        ReportDraft,
        model=settings.model_extract,
        system=DRAFT_SYSTEM,
        temperature=0.3,
    )


QA_SYSTEM = """You are the Assurance Q&A Agent for a climate-disclosure pipeline.
Answer the auditor's question strictly from the provided inventory data. Rules:
- <=120 words, factual tone.
- Append the ids of the activity records you used in "citations". Never cite a record that does not exist.
- If the data cannot answer the question, say exactly what is missing and which existing record is closest.
Return JSON: {"answer", "citations": ["A1", ...]}.
"""


def run_qa(p: Project, question: str, items: List[ActivityItem], emissions: List[EmissionResult], gaps: GapAnalysis) -> QAResponse:
    if settings.use_mock:
        return mock_ai.mock_qa(question, items, emissions, gaps)
    payload = {
        "activity_records": [i.model_dump() for i in items],
        "computed_emissions": [e.model_dump() for e in emissions],
        "known_gaps": [g.model_dump() for g in gaps.items],
    }
    return gemini.generate_structured(
        [f"Inventory data:\n{json.dumps(payload, indent=1)}\n\nAuditor question: {question}"],
        QAResponse,
        model=settings.model_fast,
        system=QA_SYSTEM,
    )
