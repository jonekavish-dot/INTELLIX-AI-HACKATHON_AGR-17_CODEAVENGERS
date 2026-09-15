"""
AgriDiff AI — LLM Analyzer
Gemini 1.5 Flash with structured JSON output and strict evidence grounding.
BIT-AI-001 | AGR-17 | Team CODEAVENGERS

Anti-hallucination design:
1. LLM only receives isolated old/new text passages.
2. Must cite exact substrings for old_evidence and new_evidence.
3. If absent or ambiguous -> INSUFFICIENT_EVIDENCE / NOT_FOUND / UNCERTAIN.
4. Schema validation and deterministic fallback on timeout or error.
"""

import os
import json
import asyncio
import logging
import re
from typing import List, Dict, Optional

logger = logging.getLogger("agridiff.llm")

LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
LLM_MAX_CONCURRENT = int(os.getenv("LLM_MAX_CONCURRENT", "5"))

CATEGORIES = [
    "Eligibility", "Financial", "Deadline", "Documentation",
    "Procedure", "Beneficiary", "LandRecord", "Other"
]
SEVERITIES = ["HIGH", "MEDIUM", "LOW"]
CHANGE_TYPES = ["MODIFIED", "ADDED", "REMOVED", "UNCHANGED", "SEMANTICALLY_EQUIVALENT"]


# ── Prompts ────────────────────────────────────────────────────────────────────

MODIFIED_PROMPT = """You are an authoritative agricultural policy and legal land-record analyst comparing two versions of a document.

Analyze what changed between the OLD and NEW versions of this passage.

CRITICAL RULES:
1. Base your analysis ONLY on the text provided. Do NOT add outside knowledge.
2. Do NOT invent or assume seller/buyer relationships or ownership unless explicitly stated.
3. If figures or dates changed, identify the specific field, old value, and new value.
4. old_evidence and new_evidence MUST be EXACT substrings from the provided text.
5. If wording changed but the legal/procedural meaning is identical, set change_type to "SEMANTICALLY_EQUIVALENT".

SECTION: {section_title}

OLD TEXT:
\"\"\"
{old_text}
\"\"\"

NEW TEXT:
\"\"\"
{new_text}
\"\"\"

Return ONLY valid JSON matching this schema:
{{
  "change_type": "MODIFIED" | "SEMANTICALLY_EQUIVALENT" | "UNCHANGED",
  "category": "Eligibility" | "Financial" | "Deadline" | "Documentation" | "Procedure" | "Beneficiary" | "LandRecord" | "Other",
  "field": "field_name or null",
  "old_value": "old value or null",
  "new_value": "new value or null",
  "summary": "One sentence describing exactly what changed",
  "interpretation": "One sentence explaining legal/practical meaning to farmers or administrators",
  "impact": "HIGH" | "MEDIUM" | "LOW",
  "old_evidence": "Exact quote from OLD TEXT, or INSUFFICIENT_EVIDENCE",
  "new_evidence": "Exact quote from NEW TEXT, or INSUFFICIENT_EVIDENCE",
  "confidence": 0.0 to 1.0
}}"""

ADDED_PROMPT = """You are an authoritative agricultural policy and land-record analyst.
The following passage was ADDED in the new version.

CRITICAL RULES:
1. Base your analysis ONLY on the text below.
2. new_evidence MUST be an exact substring from NEW TEXT.

SECTION: {section_title}

NEW TEXT (ADDED):
\"\"\"
{new_text}
\"\"\"

Return ONLY valid JSON:
{{
  "change_type": "ADDED",
  "category": "Eligibility" | "Financial" | "Deadline" | "Documentation" | "Procedure" | "Beneficiary" | "LandRecord" | "Other",
  "field": "field_name or null",
  "old_value": null,
  "new_value": "new value or null",
  "summary": "One sentence stating what was added",
  "interpretation": "One sentence explaining practical significance of this addition",
  "impact": "HIGH" | "MEDIUM" | "LOW",
  "old_evidence": "NOT_PRESENT",
  "new_evidence": "Exact quote from NEW TEXT",
  "confidence": 0.0 to 1.0
}}"""

REMOVED_PROMPT = """You are an authoritative agricultural policy and land-record analyst.
The following passage existed in the old version but was REMOVED in the new version.

CRITICAL RULES:
1. Base your analysis ONLY on the text below.
2. old_evidence MUST be an exact substring from OLD TEXT.

SECTION: {section_title}

OLD TEXT (REMOVED):
\"\"\"
{old_text}
\"\"\"

Return ONLY valid JSON:
{{
  "change_type": "REMOVED",
  "category": "Eligibility" | "Financial" | "Deadline" | "Documentation" | "Procedure" | "Beneficiary" | "LandRecord" | "Other",
  "field": "field_name or null",
  "old_value": "old value or null",
  "new_value": null,
  "summary": "One sentence stating what was removed",
  "interpretation": "One sentence explaining the effect of removing this provision",
  "impact": "HIGH" | "MEDIUM" | "LOW",
  "old_evidence": "Exact quote from OLD TEXT",
  "new_evidence": "NOT_PRESENT",
  "confidence": 0.0 to 1.0
}}"""


# ── Gemini Client Setup ────────────────────────────────────────────────────────

def _get_gemini_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(LLM_MODEL)
    except Exception as e:
        logger.error(f"Gemini initialization error: {e}")
        return None


async def _call_gemini(prompt: str) -> Optional[Dict]:
    model = _get_gemini_model()
    if model is None:
        return None

    for attempt in range(2):
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: model.generate_content(prompt)),
                timeout=LLM_TIMEOUT,
            )
            raw = response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            data = json.loads(raw.strip())
            return _validate_llm_fields(data)
        except Exception as e:
            logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(1)

    return None


def _validate_llm_fields(data: Dict) -> Dict:
    if data.get("category") not in CATEGORIES:
        data["category"] = "Other"
    if data.get("impact") not in SEVERITIES:
        data["impact"] = "MEDIUM"
    if data.get("change_type") not in CHANGE_TYPES:
        data["change_type"] = "MODIFIED"
    conf = data.get("confidence", 0.8)
    if not isinstance(conf, (int, float)):
        conf = 0.8
    data["confidence"] = max(0.0, min(1.0, float(conf)))
    return data


# ── Deterministic Fallback Generator ──────────────────────────────────────────

def _deterministic_fallback(pair: Dict) -> Dict:
    """
    High-precision deterministic rule-based analysis used when LLM is unavailable
    or for deterministic change types.
    """
    pre_type = pair.get("change_type_pre", "MODIFIED")
    old_c = pair.get("old_chunk")
    new_c = pair.get("new_chunk")
    old_txt = old_c["text"] if old_c else ""
    new_txt = new_c["text"] if new_c else ""
    sec = (old_c or new_c or {}).get("section_title", "Document Section")
    sec_lower = sec.lower()

    # Determine category
    category = "Other"
    if any(k in sec_lower for k in ["eligib", "land holding", "holding limit", "acre", "hectare"]):
        category = "Eligibility"
    elif any(k in sec_lower for k in ["financ", "subsid", "amount", "assistance", "payment", "rupee", "rs"]):
        category = "Financial"
    elif any(k in sec_lower for k in ["deadline", "due date", "submission", "validity"]):
        category = "Deadline"
    elif any(k in sec_lower for k in ["document", "certificate", "patta", "passbook", "aadhaar", "record"]):
        category = "Documentation"
    elif any(k in sec_lower for k in ["procedure", "process", "register", "verification", "portal"]):
        category = "Procedure"
    elif any(k in sec_lower for k in ["beneficiar", "fpo", "farmer", "cooperative"]):
        category = "Beneficiary"
    elif any(k in sec_lower for k in ["patta", "survey", "land record", "chitta", "adangal"]):
        category = "LandRecord"

    # Determine impact
    impact = "MEDIUM"
    if category in ["Eligibility", "Financial", "Deadline", "LandRecord"]:
        impact = "HIGH"
    elif pre_type in ["UNCHANGED", "SEMANTICALLY_EQUIVALENT"]:
        impact = "LOW"

    # Formulate summary and quotes
    if pre_type == "UNCHANGED":
        summary = f"Section '{sec}' remained identical across document versions."
        interp = "No operational or legal change."
        old_ev = old_txt[:100] if old_txt else "NOT_PRESENT"
        new_ev = new_txt[:100] if new_txt else "NOT_PRESENT"
        conf = 1.0
    elif pre_type == "SEMANTICALLY_EQUIVALENT":
        summary = f"Section '{sec}' reworded with equivalent meaning."
        interp = "Wording adjusted without altering substantive requirements or entitlements."
        old_ev = old_txt[:120] if old_txt else "NOT_PRESENT"
        new_ev = new_txt[:120] if new_txt else "NOT_PRESENT"
        conf = 0.95
    elif pre_type == "ADDED":
        summary = f"New provision added under '{sec}'."
        interp = "New condition or requirement introduced into the document."
        old_ev = "NOT_PRESENT"
        new_ev = new_txt[:150] if new_txt else "INSUFFICIENT_EVIDENCE"
        conf = 0.90
    elif pre_type == "REMOVED":
        summary = f"Provision removed from '{sec}'."
        interp = "Previous condition or requirement is no longer in effect."
        old_ev = old_txt[:150] if old_txt else "INSUFFICIENT_EVIDENCE"
        new_ev = "NOT_PRESENT"
        conf = 0.90
    else:  # MODIFIED
        summary = f"Content modified under '{sec}'."
        interp = "Substantive changes detected affecting administrative requirements."
        old_ev = old_txt[:120] if old_txt else "INSUFFICIENT_EVIDENCE"
        new_ev = new_txt[:120] if new_txt else "INSUFFICIENT_EVIDENCE"
        conf = 0.85

    return {
        "change_type": pre_type,
        "category": category,
        "field": None,
        "old_value": None,
        "new_value": None,
        "summary": summary,
        "interpretation": interp,
        "impact": impact,
        "old_evidence": old_ev,
        "new_evidence": new_ev,
        "confidence": conf,
    }


# ── Main Entry Point ──────────────────────────────────────────────────────────

async def analyze_changes(pairs: List[Dict]) -> List[Dict]:
    """
    Analyzes aligned pairs.
    Calls Gemini for MODIFIED, ADDED, REMOVED where suitable.
    Uses deterministic rules for UNCHANGED or if Gemini is absent.
    """
    has_gemini = os.getenv("GEMINI_API_KEY") not in [None, "", "your_gemini_api_key_here"]
    semaphore = asyncio.Semaphore(LLM_MAX_CONCURRENT)

    async def analyze_single(pair: Dict) -> Dict:
        pre_type = pair.get("change_type_pre", "MODIFIED")
        
        # Don't spend LLM calls on identical text
        if pre_type == "UNCHANGED":
            pair["llm_result"] = _deterministic_fallback(pair)
            return pair

        if has_gemini and pre_type in ["MODIFIED", "ADDED", "REMOVED"]:
            async with semaphore:
                old_t = pair["old_chunk"]["text"] if pair.get("old_chunk") else ""
                new_t = pair["new_chunk"]["text"] if pair.get("new_chunk") else ""
                sec = (pair.get("old_chunk") or pair.get("new_chunk") or {}).get("section_title", "")
                
                if pre_type == "MODIFIED":
                    prompt = MODIFIED_PROMPT.format(section_title=sec, old_text=old_t[:1500], new_text=new_t[:1500])
                elif pre_type == "ADDED":
                    prompt = ADDED_PROMPT.format(section_title=sec, new_text=new_t[:1500])
                else:
                    prompt = REMOVED_PROMPT.format(section_title=sec, old_text=old_t[:1500])

                res = await _call_gemini(prompt)
                if res:
                    pair["llm_result"] = res
                    return pair

        # Deterministic fallback
        pair["llm_result"] = _deterministic_fallback(pair)
        return pair

    results = await asyncio.gather(*[analyze_single(p) for p in pairs])
    return results
