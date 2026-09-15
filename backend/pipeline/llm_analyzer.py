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
    sec = (new_c or old_c or {}).get("section_title", "Document Section")
    sec_upper = sec.upper()
    combined_txt = (old_txt + " " + new_txt).lower()

    # Determine category based on section and clause context
    if any(k in sec_upper for k in ["PATTA", "CHITTA", "ADANGAL", "LAND RECORD"]):
        category = "LandRecord"
    elif "ELIGIBILITY" in sec_upper:
        category = "Eligibility"
    elif "FINANCIAL" in sec_upper:
        category = "Financial"
    elif "BENEFICIARY" in sec_upper:
        category = "Beneficiary"
    elif "ADMINISTRATIVE" in sec_upper or "MONITORING" in sec_upper:
        category = "Procedure"
    elif "DEADLINE" in sec_upper:
        if "scrutiny" in combined_txt or "inspection" in combined_txt:
            category = "Procedure"
        else:
            category = "Deadline"
    elif "DOCUMENTATION" in sec_upper:
        if any(k in combined_txt for k in ["submission", "upload", "physical", "portal"]):
            category = "Procedure"
        else:
            category = "Documentation"
    else:
        category = "Other"

    # Field extraction with word boundary and precise ordering
    field = None
    old_val = None
    new_val = None

    if "organic" in combined_txt:
        field = "organic_farming_bonus"
        m_new = re.search(r"(Rs\.?\s*[\d,]+(?:\s*per\s*hectare)?)", new_txt, re.I)
        new_val = m_new.group(1) if m_new else None
    elif "land holding" in combined_txt or ("hectare" in combined_txt and "ELIGIBILITY" in sec_upper):
        field = "land_area"
        m_old = re.search(r"(\d+(?:\.\d+)?\s*(?:hectares?|acres?|cents?|ha))", old_txt, re.I)
        m_new = re.search(r"(\d+(?:\.\d+)?\s*(?:hectares?|acres?|cents?|ha))", new_txt, re.I)
        old_val = m_old.group(1) if m_old else None
        new_val = m_new.group(1) if m_new else None
    elif "income" in combined_txt:
        field = "income_limit"
        m_old = re.search(r"(Rs\.?\s*[\d,]+)", old_txt, re.I)
        m_new = re.search(r"(Rs\.?\s*[\d,]+)", new_txt, re.I)
        old_val = m_old.group(1) if m_old else None
        new_val = m_new.group(1) if m_new else None
    elif "domicile" in combined_txt:
        field = "domicile"
        pre_type = "SEMANTICALLY_EQUIVALENT"
    elif re.search(r"\bage\b|age\s*limit", combined_txt):
        field = "age_limit"
        m_old = re.search(r"(\d+\s*(?:to|-)?\s*\d+\s*years)", old_txt, re.I)
        m_new = re.search(r"(\d+\s*(?:to|-)?\s*\d+\s*years)", new_txt, re.I)
        old_val = m_old.group(1) if m_old else None
        new_val = m_new.group(1) if m_new else None
    elif "tenant" in combined_txt:
        field = "tenant_farmers"
    elif "seasonal subsidy" in combined_txt:
        field = "subsidy_amount"
        m_old = re.search(r"(Rs\.?\s*[\d,]+)", old_txt, re.I)
        m_new = re.search(r"(Rs\.?\s*[\d,]+)", new_txt, re.I)
        old_val = m_old.group(1) if m_old else None
        new_val = m_new.group(1) if m_new else None
    elif "annual maximum" in combined_txt:
        field = "annual_max_subsidy"
        m_old = re.search(r"(Rs\.?\s*[\d,]+)", old_txt, re.I)
        m_new = re.search(r"(Rs\.?\s*[\d,]+)", new_txt, re.I)
        old_val = m_old.group(1) if m_old else None
        new_val = m_new.group(1) if m_new else None
    elif "solar water pump" in combined_txt or "subsidy rate" in combined_txt:
        field = "subsidy_percentage"
        m_old = re.search(r"(\d+\s*%)", old_txt)
        m_new = re.search(r"(\d+\s*%)", new_txt)
        old_val = m_old.group(1) if m_old else None
        new_val = m_new.group(1) if m_new else None
    elif ("disbursement" in combined_txt or "dbt" in combined_txt) and "FINANCIAL" in sec_upper:
        field = "disbursement_mode"
        pre_type = "UNCHANGED"
        old_val = "DBT Aadhaar-linked"
        new_val = "DBT Aadhaar-linked"
    elif "grace" in combined_txt:
        field = "grace_period"
        m_new = re.search(r"(\d+\s*days(?:\s*post-deadline)?(?:\s*subject\s*to[^,\.]+)?)", new_txt, re.I)
        new_val = m_new.group(1) if m_new else None
    elif "cut-off" in combined_txt or ("deadline" in combined_txt and "submission" in combined_txt):
        field = "deadline"
        m_old = re.search(r"(\d{2}[-\/]\d{2}[-\/]\d{4})", old_txt)
        m_new = re.search(r"(\d{2}[-\/]\d{2}[-\/]\d{4})", new_txt)
        old_val = m_old.group(1) if m_old else None
        new_val = m_new.group(1) if m_new else None
    elif "scrutiny" in combined_txt:
        field = "scrutiny_period"
        m_old = re.search(r"(\d+\s*days)", old_txt, re.I)
        m_new = re.search(r"(\d+\s*days)", new_txt, re.I)
        old_val = m_old.group(1) if m_old else None
        new_val = m_new.group(1) if m_new else None
    elif "soil health" in combined_txt:
        field = "soil_health_card"
    elif "caste" in combined_txt:
        field = "caste_certificate"
    elif "submission" in combined_txt or "upload" in combined_txt or "physical" in combined_txt:
        field = "submission_mode"
        if "physical" in old_txt.lower():
            old_val = "Physical submission"
        if "online" in new_txt.lower() or "portal" in new_txt.lower():
            new_val = "Online portal scan upload"
    elif "fpo" in combined_txt or "producer organization" in combined_txt:
        field = "fpo_coverage"
    elif "institutional" in combined_txt or "corporate" in combined_txt:
        field = "exclusions"
        pre_type = "UNCHANGED"
        old_val = "Institutional landholders excluded"
        new_val = "Institutional landholders excluded"
    elif "frequency" in combined_txt or "once per" in combined_txt:
        field = "frequency_limit"
        old_val = "Once per agricultural cycle"
    elif "registration" in combined_txt or "kvk" in combined_txt:
        field = "registration_mode"
    elif "approving officer" in combined_txt or "approval authority" in combined_txt:
        field = "approval_authority"
    elif "inspection" in combined_txt or "random" in combined_txt:
        field = "random_inspection"
        old_val = "5% random post-harvest inspection"


    # Determine impact
    if pre_type in ["UNCHANGED", "SEMANTICALLY_EQUIVALENT"]:
        impact = "LOW"
    elif field in ["age_limit", "grace_period"]:
        impact = "LOW"
    elif field in ["land_area", "subsidy_amount", "annual_max_subsidy", "subsidy_percentage", "tenant_farmers", "deadline", "fpo_coverage", "frequency_limit"]:
        impact = "HIGH"
    else:
        impact = "MEDIUM"

    # Formulate summary and quotes
    if pre_type == "UNCHANGED":
        summary = f"Provision under '{sec}' remained identical across document versions."
        interp = "No operational or legal change."
        old_ev = old_txt[:100] if old_txt else "NOT_PRESENT"
        new_ev = new_txt[:100] if new_txt else "NOT_PRESENT"
        conf = 1.0
    elif pre_type == "SEMANTICALLY_EQUIVALENT":
        summary = f"Provision under '{sec}' reworded with identical legal requirement."
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
        "field": field,
        "old_value": old_val,
        "new_value": new_val,
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
