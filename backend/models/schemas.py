"""
AgriDiff AI — Canonical Pydantic Schemas
Defines the shared data contract for Backend, Validation, Frontend, Evaluation, and Testing.
BIT-AI-001 | AGR-17 | Team CODEAVENGERS
"""

from typing import Optional, List, Literal, Any
from pydantic import BaseModel, Field


# ── Canonical Change Object ───────────────────────────────────────────────────

class EvidenceSpan(BaseModel):
    old_text: Optional[str] = None
    old_page: Optional[int] = None
    new_text: Optional[str] = None
    new_page: Optional[int] = None
    quote: Optional[str] = None
    status: Literal["SUPPORTED", "UNCERTAIN", "NOT_FOUND"] = "SUPPORTED"


class DetectedChange(BaseModel):
    change_id: str = Field(..., description="Canonical ID e.g. CH-001")
    section: str = Field(..., description="Section where change occurred")
    subsection: Optional[str] = Field(None, description="Subsection number if available")
    
    change_type: Literal["ADDED", "REMOVED", "MODIFIED", "UNCHANGED", "SEMANTICALLY_EQUIVALENT"] = Field(
        ..., description="Type of change"
    )
    category: Literal[
        "Eligibility", "Financial", "Deadline", "Documentation",
        "Procedure", "Beneficiary", "LandRecord", "Other"
    ] = Field(..., description="Agricultural policy / administrative domain category")
    
    field: Optional[str] = Field(None, description="Specific field name if entity-level (e.g. land_area, survey_number)")
    old_value: Optional[str] = Field(None, description="Structured old value if applicable")
    new_value: Optional[str] = Field(None, description="Structured new value if applicable")

    old_text: Optional[str] = Field(None, description="Full old source passage")
    new_text: Optional[str] = Field(None, description="Full new source passage")
    old_evidence: Optional[str] = Field(None, description="Exact verified quote from old text")
    new_evidence: Optional[str] = Field(None, description="Exact verified quote from new text")

    old_page: Optional[int] = Field(None, description="Page number in old document")
    new_page: Optional[int] = Field(None, description="Page number in new document")

    summary: str = Field(..., description="Concise one-sentence description of the change")
    interpretation: str = Field(..., description="Semantic/impact explanation bounded by source evidence")
    operational_note: Optional[str] = Field(None, description="Actionable operational guidance for field officers, verification squads, and administrators")
    impact: Literal["HIGH", "MEDIUM", "LOW"] = Field(..., description="Consequential priority")
    evidence_status: Literal["SUPPORTED", "UNCERTAIN", "NOT_FOUND"] = Field(
        "SUPPORTED", description="Strict evidence grounding status"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")

    # Document Change Unit vs Supporting Evidence Spans
    evidence_spans: List[EvidenceSpan] = Field(default_factory=list, description="Supporting evidence spans for this change")

    # Optional internal diagnostics
    textual_diff_ratio: Optional[float] = Field(None, description="Ratio of text that changed (0-1)")
    semantic_similarity: Optional[float] = Field(None, description="Cosine similarity score (0-1)")


# ── Field / Entity Change Object (Structured comparison) ─────────────────────

class FieldChange(BaseModel):
    field_id: str = Field(..., description="Unique field ID e.g. FLD-001")
    field_name: str = Field(..., description="e.g. land_area, survey_number, patta_holder")
    display_label: str = Field(..., description="Human readable label e.g. 'Land Area'")
    old_value: Optional[str] = Field(None, description="Old value or NOT_FOUND")
    new_value: Optional[str] = Field(None, description="New value or NOT_FOUND")
    change_type: Literal["ADDED", "REMOVED", "MODIFIED", "UNCHANGED"] = Field(...)
    old_page: Optional[int] = None
    new_page: Optional[int] = None
    evidence_status: Literal["SUPPORTED", "UNCERTAIN", "NOT_FOUND"] = "SUPPORTED"
    notes: Optional[str] = None


# ── Summary Stats ──────────────────────────────────────────────────────────────

class SeverityBreakdown(BaseModel):
    HIGH: int = 0
    MEDIUM: int = 0
    LOW: int = 0


class CategoryBreakdown(BaseModel):
    Eligibility: int = 0
    Financial: int = 0
    Deadline: int = 0
    Documentation: int = 0
    Procedure: int = 0
    Beneficiary: int = 0
    LandRecord: int = 0
    Other: int = 0


class SummaryStats(BaseModel):
    total_textual_differences: int = 0
    total_all_changes: int = 0        # Exhaustive count
    total_impact_changes: int = 0     # Prioritized count (HIGH/MEDIUM)
    total_field_changes: int = 0      # Structured entity changes
    added: int = 0
    removed: int = 0
    modified: int = 0
    unchanged: int = 0
    semantically_equivalent: int = 0
    by_severity: SeverityBreakdown = Field(default_factory=SeverityBreakdown)
    by_category: CategoryBreakdown = Field(default_factory=CategoryBreakdown)


# ── Document Metadata ──────────────────────────────────────────────────────────

class DocumentMeta(BaseModel):
    filename: str
    pages: int
    sections_detected: int = 0
    chunks: int = 0


class DocumentPair(BaseModel):
    old: DocumentMeta
    new: DocumentMeta


# ── Evaluation Metadata ────────────────────────────────────────────────────────

class EvaluationMeta(BaseModel):
    avg_confidence: float = 0.0
    evidence_grounding_rate: float = 1.0
    llm_model_used: str = "gemini-1.5-flash"
    fallback_used: bool = False


# ── API Responses ──────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class CompareResponse(BaseModel):
    job_id: str
    status: str
    message: str


class StatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str


class ResultsResponse(BaseModel):
    job_id: str
    status: str
    processing_time_seconds: Optional[float] = None
    documents: DocumentPair
    summary: SummaryStats
    all_changes: List[DetectedChange]       # EXHAUSTIVE: every detected difference
    impact_changes: List[DetectedChange]    # IMPACT VIEW: prioritized consequential changes
    field_changes: List[FieldChange]        # STRUCTURED ENTITY / LAND RECORD VIEW
    evaluation: EvaluationMeta
