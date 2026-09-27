from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SourceRef(BaseModel):
    file_name: str
    page: Optional[int] = None
    excerpt: str = ""


class ActivityItem(BaseModel):
    id: str = ""
    category: str
    description: str
    quantity: float
    unit: str
    period: Optional[str] = None
    location: Optional[str] = None
    scope_guess: Optional[int] = None
    confidence: float = 0.5
    source: SourceRef
    status: str = "pending"  # pending | confirmed | edited | rejected


class ExtractionResult(BaseModel):
    items: List[ActivityItem] = Field(default_factory=list)


class MappingResultRow(BaseModel):
    item_id: str
    factor_id: str
    quantity_in_factor_unit: float
    scope: int
    rationale: str = ""


class MappingResult(BaseModel):
    results: List[MappingResultRow] = Field(default_factory=list)


class EmissionResult(BaseModel):
    item_id: str
    factor_id: str
    factor_name: str
    quantity_in_factor_unit: float
    factor_value: float
    factor_unit: str
    co2e_kg: float
    scope: int
    rationale: str = ""


class GapItem(BaseModel):
    requirement: str
    description: str
    severity: str = "medium"  # high | medium | low
    suggestion: str = ""


class GapAnalysis(BaseModel):
    items: List[GapItem] = Field(default_factory=list)


class ReportSection(BaseModel):
    heading: str
    content: str


class ReportDraft(BaseModel):
    title: str
    period: str
    summary: str
    sections: List[ReportSection] = Field(default_factory=list)


class QAResponse(BaseModel):
    answer: str
    citations: List[str] = Field(default_factory=list)


class AuditEvent(BaseModel):
    ts: str
    stage: str
    detail: str
    duration_ms: Optional[int] = None


class Document(BaseModel):
    id: str
    file_name: str
    mime_type: str
    size: int
    text: Optional[str] = None  # populated for text-like inputs


class Project(BaseModel):
    id: str
    name: str
    created_at: str
    documents: List[Document] = Field(default_factory=list)
    activities: List[ActivityItem] = Field(default_factory=list)
    emissions: List[EmissionResult] = Field(default_factory=list)
    gaps: List[GapItem] = Field(default_factory=list)
    report: Optional[ReportDraft] = None
    audit: List[AuditEvent] = Field(default_factory=list)
