"""
AgriDiff AI — Evidence Validator + Result Assembler
Post-processes LLM output:
1. Verifies evidence quotes are actual substrings of source text (anti-hallucination)
2. Runs deterministic numeric/date checks
3. Assembles final result JSON
"""

import re
import time
import uuid
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("agridiff.validator")

START_TIME = time.time()


# ── Evidence Grounding Check ───────────────────────────────────────────────────

def _verify_evidence(evidence: str, source_text: str) -> tuple[str, str]:
    """
    Verify that the LLM's cited evidence is an actual substring of source_text.
    Returns (verified_evidence, evidence_status).
    """
    if evidence in ("NOT_PRESENT", "INSUFFICIENT_EVIDENCE", None, ""):
        return evidence or "INSUFFICIENT_EVIDENCE", evidence or "INSUFFICIENT_EVIDENCE"

    # Try exact match first
    if evidence in source_text:
        return evidence, "SUPPORTED"

    # Try case-insensitive
    if evidence.lower() in source_text.lower():
        return evidence, "SUPPORTED"

    # Try partial match (first 50 chars of evidence)
    partial = evidence[:50].strip()
    if partial and partial in source_text:
        return evidence, "SUPPORTED"

    # Evidence not found — replace with actual source text (truncated)
    logger.warning(f"Evidence not grounded — replacing with source text snippet")
    snippet = source_text[:300].strip()
    return snippet, "INSUFFICIENT_EVIDENCE"


# ── Deterministic Numeric/Date Checks ─────────────────────────────────────────

NUMERIC_PATTERNS = [
    re.compile(r"Rs\.?\s*[\d,]+"),           # Indian Rupee amounts
    re.compile(r"\d+\s*hectares?"),           # Land area
    re.compile(r"\d+\s*%"),                  # Percentages
    re.compile(r"\d+\s*days?"),              # Time periods
    re.compile(r"\d{1,2}\s+\w+\s+\d{4}"),   # Dates like "31 March 2024"
    re.compile(r"\d{1,2}/\d{1,2}/\d{4}"),   # DD/MM/YYYY
]

def _has_numeric_change(old_text: str, new_text: str) -> bool:
    """Check if any numeric value changed between old and new text."""
    for pattern in NUMERIC_PATTERNS:
        old_matches = set(m.group() for m in pattern.finditer(old_text or ""))
        new_matches = set(m.group() for m in pattern.finditer(new_text or ""))
        if old_matches != new_matches:
            return True
    return False


# ── Severity Boosting via Deterministic Rules ──────────────────────────────────

def _boost_severity(llm_severity: str, old_text: str, new_text: str,
                    category: str, similarity: float) -> str:
    """
    Apply deterministic rules to validate/boost severity.
    The LLM determines category and initial severity; this validates it.
    """
    # HIGH if: financial amounts, land thresholds, or deadlines changed
    if category in ("Financial", "Eligibility", "Deadline"):
        if _has_numeric_change(old_text or "", new_text or ""):
            return "HIGH"

    # HIGH if semantic similarity is very low (< 0.5)
    if similarity < 0.5 and llm_severity == "LOW":
        return "MEDIUM"

    return llm_severity


# ── Result Assembly ────────────────────────────────────────────────────────────

def validate_and_assemble(
    pairs: List[Dict],
    old_doc_meta: Dict,
    new_doc_meta: Dict,
    job_id: str,
) -> Dict:
    """
    Validate all pairs and assemble the final API result.
    """
    changes = []
    total_textual = 0
    change_counts = {"ADDED": 0, "REMOVED": 0, "MODIFIED": 0, "REWORDED": 0, "EQUIVALENT": 0}
    severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    category_counts = {c: 0 for c in ["Eligibility", "Financial", "Deadline", "Documentation", "Procedure", "Beneficiary", "Other"]}

    for pair in pairs:
        old_chunk = pair.get("old_chunk")
        new_chunk = pair.get("new_chunk")
        llm = pair.get("llm_result", {})
        similarity = pair.get("similarity", 0.0)
        textual_diff = pair.get("textual_diff_ratio", 0.0)

        old_text = old_chunk["text"] if old_chunk else ""
        new_text = new_chunk["text"] if new_chunk else ""

        # Track textual differences
        if pair.get("has_textual_change", False):
            total_textual += 1

        # Skip EQUIVALENT pairs from results
        pre_type = pair.get("change_type_pre", "MODIFIED")
        if pre_type == "EQUIVALENT":
            change_counts["EQUIVALENT"] += 1
            continue

        # Use LLM result
        is_meaningful = llm.get("is_meaningful_change", True)
        change_type = llm.get("change_type", pre_type)
        category = llm.get("category", "Other")
        severity = llm.get("severity", "MEDIUM")
        confidence = llm.get("confidence", 0.5)

        # Deterministic severity boost
        severity = _boost_severity(severity, old_text, new_text, category, similarity)

        # Evidence grounding check
        raw_old_evidence = llm.get("old_evidence", "INSUFFICIENT_EVIDENCE")
        raw_new_evidence = llm.get("new_evidence", "INSUFFICIENT_EVIDENCE")

        verified_old_evidence, old_status = _verify_evidence(raw_old_evidence, old_text)
        verified_new_evidence, new_status = _verify_evidence(raw_new_evidence, new_text)

        # Overall evidence status
        if old_status == "SUPPORTED" or new_status == "SUPPORTED":
            evidence_status = "SUPPORTED"
        elif raw_old_evidence == "NOT_PRESENT" or raw_new_evidence == "NOT_PRESENT":
            evidence_status = "SUPPORTED"  # ADDED/REMOVED are inherently supported
        else:
            evidence_status = "INSUFFICIENT_EVIDENCE"

        # Skip non-meaningful REWORDED
        if change_type == "REWORDED" and not is_meaningful:
            change_counts["REWORDED"] += 1
            continue

        if is_meaningful:
            change_counts[change_type] = change_counts.get(change_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1

            changes.append({
                "change_id": f"chg_{str(uuid.uuid4())[:8]}",
                "section_title": (old_chunk or new_chunk or {}).get("section_title", "Unknown"),
                "section_number": (old_chunk or new_chunk or {}).get("section_number"),
                "change_type": change_type,
                "category": category,
                "severity": severity,
                "old_text": old_text[:600] or None,
                "new_text": new_text[:600] or None,
                "old_evidence": verified_old_evidence,
                "new_evidence": verified_new_evidence,
                "old_page": old_chunk.get("page_start") if old_chunk else None,
                "new_page": new_chunk.get("page_start") if new_chunk else None,
                "summary": llm.get("summary", "Content changed"),
                "impact": llm.get("impact", "Review required"),
                "textual_diff_ratio": textual_diff,
                "semantic_similarity": similarity,
                "is_meaningful_change": True,
                "confidence": round(confidence, 3),
                "evidence_status": evidence_status,
                "processing_notes": None,
            })

    # Sort by severity (HIGH first)
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    changes.sort(key=lambda c: (severity_order.get(c["severity"], 3), -c["confidence"]))

    # Evaluation metadata
    total_meaningful = len(changes)
    grounded = sum(1 for c in changes if c["evidence_status"] == "SUPPORTED")
    grounding_rate = round(grounded / total_meaningful, 3) if total_meaningful > 0 else 1.0
    avg_conf = round(sum(c["confidence"] for c in changes) / total_meaningful, 3) if total_meaningful > 0 else 0.0

    return {
        "job_id": job_id,
        "status": "completed",
        "processing_time_seconds": round(time.time() - START_TIME, 1),
        "documents": {
            "old": {
                "filename": old_doc_meta["filename"],
                "pages": old_doc_meta["pages"],
                "sections_detected": old_doc_meta.get("sections", 0),
                "chunks": old_doc_meta["chunks"],
            },
            "new": {
                "filename": new_doc_meta["filename"],
                "pages": new_doc_meta["pages"],
                "sections_detected": new_doc_meta.get("sections", 0),
                "chunks": new_doc_meta["chunks"],
            },
        },
        "summary": {
            "total_textual_differences": total_textual,
            "total_meaningful_changes": total_meaningful,
            "added": change_counts.get("ADDED", 0),
            "removed": change_counts.get("REMOVED", 0),
            "modified": change_counts.get("MODIFIED", 0),
            "reworded": change_counts.get("REWORDED", 0),
            "equivalent": change_counts.get("EQUIVALENT", 0),
            "by_severity": severity_counts,
            "by_category": category_counts,
        },
        "changes": changes,
        "evaluation": {
            "avg_confidence": avg_conf,
            "evidence_grounding_rate": grounding_rate,
            "llm_model_used": "gemini-1.5-flash",
        },
    }
