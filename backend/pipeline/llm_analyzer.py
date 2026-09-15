"""
AgriDiff AI — LLM Analyzer
Gemini 1.5 Flash with structured JSON output.
Provides Level 2 (semantic) and Level 3 (impact) intelligence.

Anti-hallucination design:
- LLM only sees supplied old/new text snippets
- Must return INSUFFICIENT_EVIDENCE if text doesn't support the claim
- JSON schema validated before acceptance
- Falls back to deterministic defaults if LLM fails
"""

import os
import json
import asyncio
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("agridiff.llm")

LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
LLM_MAX_CONCURRENT = int(os.getenv("LLM_MAX_CONCURRENT", "5"))

CATEGORIES = ["Eligibility", "Financial", "Deadline", "Documentation", "Procedure", "Beneficiary", "Other"]
SEVERITIES = ["HIGH", "MEDIUM", "LOW"]
CHANGE_TYPES = ["MODIFIED", "ADDED", "REMOVED", "REWORDED", "EQUIVALENT"]

# ── Default fallback response ──────────────────────────────────────────────────
FALLBACK_RESPONSE = {
    "is_meaningful_change": True,
    "change_type": "MODIFIED",
    "category": "Other",
    "severity": "MEDIUM",
    "summary": "Content has changed between document versions",
    "impact": "Review this section for operational implications",
    "old_evidence": "INSUFFICIENT_EVIDENCE",
    "new_evidence": "INSUFFICIENT_EVIDENCE",
    "confidence": 0.4,
}


# ── Prompts ────────────────────────────────────────────────────────────────────

MODIFIED_PROMPT = """You are an expert agricultural policy analyst reviewing two versions of a government agricultural scheme document.

Your task: analyze what changed between the OLD and NEW versions of this passage.

CRITICAL RULES:
1. Base your analysis ONLY on the text provided. Do NOT add outside knowledge.
2. If the text does not support a specific claim, return INSUFFICIENT_EVIDENCE for that field.
3. Do NOT hallucinate financial figures, dates, names, or conditions not in the text.
4. old_evidence and new_evidence MUST be exact substrings from the provided texts.

SECTION: {section_title}

OLD TEXT:
\"\"\"
{old_text}
\"\"\"

NEW TEXT:
\"\"\"
{new_text}
\"\"\"

Return ONLY valid JSON, no markdown, no explanation:
{{
  "is_meaningful_change": true or false,
  "change_type": "MODIFIED" | "ADDED" | "REMOVED" | "REWORDED" | "EQUIVALENT",
  "category": "Eligibility" | "Financial" | "Deadline" | "Documentation" | "Procedure" | "Beneficiary" | "Other",
  "severity": "HIGH" | "MEDIUM" | "LOW",
  "summary": "One sentence: what specifically changed",
  "impact": "One sentence: why this matters to farmers or beneficiaries",
  "old_evidence": "Exact quote from OLD TEXT, or INSUFFICIENT_EVIDENCE",
  "new_evidence": "Exact quote from NEW TEXT, or INSUFFICIENT_EVIDENCE",
  "confidence": 0.0 to 1.0
}}"""

ADDED_PROMPT = """You are an expert agricultural policy analyst.

The following text is a NEW ADDITION to an agricultural policy document. There is no corresponding text in the old version.

CRITICAL RULES:
1. Base your analysis ONLY on the text below. Do NOT add outside knowledge.
2. If the text is insufficient to classify, return INSUFFICIENT_EVIDENCE.

SECTION: {section_title}

NEW TEXT (ADDED):
\"\"\"
{new_text}
\"\"\"

Return ONLY valid JSON:
{{
  "is_meaningful_change": true or false,
  "change_type": "ADDED",
  "category": "Eligibility" | "Financial" | "Deadline" | "Documentation" | "Procedure" | "Beneficiary" | "Other",
  "severity": "HIGH" | "MEDIUM" | "LOW",
  "summary": "One sentence: what was added",
  "impact": "One sentence: why this addition matters",
  "old_evidence": "NOT_PRESENT",
  "new_evidence": "Exact quote from NEW TEXT, or INSUFFICIENT_EVIDENCE",
  "confidence": 0.0 to 1.0
}}"""

REMOVED_PROMPT = """You are an expert agricultural policy analyst.

The following text EXISTED in the old version of an agricultural policy document but has been REMOVED in the new version.

CRITICAL RULES:
1. Base your analysis ONLY on the text below. Do NOT add outside knowledge.
2. If the text is insufficient to classify, return INSUFFICIENT_EVIDENCE.

SECTION: {section_title}

OLD TEXT (REMOVED):
\"\"\"
{old_text}
\"\"\"

Return ONLY valid JSON:
{{
  "is_meaningful_change": true or false,
  "change_type": "REMOVED",
  "category": "Eligibility" | "Financial" | "Deadline" | "Documentation" | "Procedure" | "Beneficiary" | "Other",
  "severity": "HIGH" | "MEDIUM" | "LOW",
  "summary": "One sentence: what was removed",
  "impact": "One sentence: why this removal matters",
  "old_evidence": "Exact quote from OLD TEXT, or INSUFFICIENT_EVIDENCE",
  "new_evidence": "NOT_PRESENT",
  "confidence": 0.0 to 1.0
}}"""


# ── Gemini Client ──────────────────────────────────────────────────────────────

def _get_gemini():
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(LLM_MODEL)
    except Exception as e:
        logger.error(f"Failed to initialize Gemini: {e}")
        return None


async def _call_llm(prompt: str) -> Optional[Dict]:
    """Call Gemini with retry. Returns parsed dict or None."""
    model = _get_gemini()
    if model is None:
        return None

    for attempt in range(2):
        try:
            # Run synchronous Gemini call in thread pool
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: model.generate_content(prompt)),
                timeout=LLM_TIMEOUT,
            )
            text = response.text.strip()

            # Strip markdown code fences if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]

            parsed = json.loads(text.strip())
            return _validate_llm_response(parsed)

        except asyncio.TimeoutError:
            logger.warning(f"LLM timeout (attempt {attempt + 1})")
        except json.JSONDecodeError as e:
            logger.warning(f"LLM JSON parse error (attempt {attempt + 1}): {e}")
        except Exception as e:
            logger.warning(f"LLM call failed (attempt {attempt + 1}): {e}")

        await asyncio.sleep(1)

    return None


def _validate_llm_response(data: Dict) -> Dict:
    """Validate and sanitize LLM response against expected schema."""
    if data.get("category") not in CATEGORIES:
        data["category"] = "Other"
    if data.get("severity") not in SEVERITIES:
        data["severity"] = "MEDIUM"
    if data.get("change_type") not in CHANGE_TYPES:
        data["change_type"] = "MODIFIED"
    if not isinstance(data.get("confidence"), (int, float)):
        data["confidence"] = 0.5
    data["confidence"] = max(0.0, min(1.0, float(data["confidence"])))
    return data


# ── Main export ────────────────────────────────────────────────────────────────

async def analyze_changes(pairs: List[Dict]) -> List[Dict]:
    """
    Run LLM analysis on pairs that need semantic interpretation.
    EQUIVALENT and REWORDED pairs skip LLM (deterministic decision).
    """
    # Identify pairs needing LLM
    needs_llm = [
        p for p in pairs
        if p["change_type_pre"] in ("MODIFIED", "ADDED", "REMOVED")
    ]
    skip_llm = [
        p for p in pairs
        if p["change_type_pre"] in ("EQUIVALENT", "REWORDED")
    ]

    logger.info(f"LLM analysis: {len(needs_llm)} pairs to analyze, {len(skip_llm)} skipped (equivalent/reworded)")

    # Process in batches to respect rate limits
    semaphore = asyncio.Semaphore(LLM_MAX_CONCURRENT)

    async def analyze_one(pair: Dict) -> Dict:
        async with semaphore:
            llm_result = await _analyze_pair(pair)
            pair["llm_result"] = llm_result
            return pair

    analyzed = await asyncio.gather(*[analyze_one(p) for p in needs_llm])

    # Add default for skipped pairs
    for p in skip_llm:
        p["llm_result"] = {
            "is_meaningful_change": False,
            "change_type": p["change_type_pre"],
            "category": "Other",
            "severity": "LOW",
            "summary": "Content appears unchanged or only rephrased",
            "impact": "No significant operational impact expected",
            "old_evidence": "INSUFFICIENT_EVIDENCE",
            "new_evidence": "INSUFFICIENT_EVIDENCE",
            "confidence": 0.9,
        }

    return list(analyzed) + skip_llm


async def _analyze_pair(pair: Dict) -> Dict:
    """Dispatch to the right prompt based on change type."""
    change_type = pair["change_type_pre"]
    old_text = pair["old_chunk"]["text"] if pair["old_chunk"] else ""
    new_text = pair["new_chunk"]["text"] if pair["new_chunk"] else ""
    section = (
        pair["old_chunk"]["section_title"] if pair["old_chunk"]
        else pair["new_chunk"]["section_title"] if pair["new_chunk"]
        else "Unknown Section"
    )

    if change_type == "MODIFIED":
        prompt = MODIFIED_PROMPT.format(section_title=section, old_text=old_text[:1500], new_text=new_text[:1500])
    elif change_type == "ADDED":
        prompt = ADDED_PROMPT.format(section_title=section, new_text=new_text[:1500])
    elif change_type == "REMOVED":
        prompt = REMOVED_PROMPT.format(section_title=section, old_text=old_text[:1500])
    else:
        return dict(FALLBACK_RESPONSE)

    result = await _call_llm(prompt)
    if result is None:
        logger.warning(f"LLM failed for pair in '{section}' — using fallback")
        return dict(FALLBACK_RESPONSE)

    return result
