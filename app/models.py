from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    clinical_note: str = Field(..., min_length=10)


class RedactionItem(BaseModel):
    category: str
    original: str
    replacement: str
    start: int
    end: int


class RiskFactor(BaseModel):
    factor_id: str
    label: str
    weight: float
    present: bool
    detail: str


class AnalyzeResponse(BaseModel):
    original_text: str
    redacted_text: str
    redactions: list[RedactionItem]
    redaction_count: int
    risk_score: float
    risk_level: str
    risk_factors: list[RiskFactor]
    summary: str


class SampleInfo(BaseModel):
    id: str
    title: str
    description: str
