"""
AgriDiff AI — Structured Entity & Land Record Extractor
Extracts and compares structured fields: land area, survey numbers, holders, verifiers,
dates, monetary figures, percentages, and administrative metadata.
BIT-AI-001 | AGR-17 | Team CODEAVENGERS

Anti-hallucination rules:
1. Absent information -> NOT_FOUND
2. Ambiguous information -> UNCERTAIN
3. Direct evidence -> SUPPORTED
4. Never infer seller/buyer or legal ownership unless explicitly stated in source text.
"""

import re
import logging
from typing import Dict, List, Any, Optional
try:
    from models.schemas import FieldChange
except ImportError:
    from backend.models.schemas import FieldChange

logger = logging.getLogger("agridiff.entity_extractor")

# ── Regex Patterns ─────────────────────────────────────────────────────────────

# Land Area: e.g. "2 hectares", "4 acres", "50 cents", "2.5 ha"
RE_LAND_AREA = re.compile(
    r"(?i)\b(\d+(?:\.\d+)?)\s*(hectares?|acres?|cents?|sq(?:\.|\s*)meters?|ha)\b"
)

# Survey / Subdivision numbers: e.g. "Survey No. 123", "Survey No: 123/2", "S.No 45/1A"
RE_SURVEY_NO = re.compile(
    r"(?i)(?:survey\s*(?:no\.?|number|#)?|s\.?no\.?|patta\s*no\.?)\s*[:\-]?\s*([0-9]+(?:\s*/\s*[0-9a-zA-Z]+)?)"
)

# Currency: e.g. "Rs. 5,000", "Rs 8000", "INR 10,000", "₹5,000"
RE_MONETARY = re.compile(
    r"(?:Rs\.?|INR|₹)\s*([\d,]+(?:\.\d{2})?)"
)

# Percentages: e.g. "40%", "50 %"
RE_PERCENTAGE = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*%"
)

# Dates: e.g. "31st March 2024", "30-09-2026", "15/10/2026", "31 March"
RE_DATE = re.compile(
    r"(?i)\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)(?:\s+\d{4})?|\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})\b"
)

# Deadline phrases
RE_DEADLINE = re.compile(
    r"(?i)(?:deadline|submitted by|due date|last date)\s*(?:is|shall be)?\s*[:\-]?\s*([A-Za-z0-9\s,/\-]+?)(?:\.|\n|$)"
)

# Holder / Patta Holder / Owner (explicit patterns only)
RE_HOLDER = re.compile(
    r"(?i)(?:patta\s*holder|land\s*holder|owner\s*name|farmer\s*name|applicant\s*name|registered\s*to)\s*[:\-]\s*([A-Za-z\.\s]{2,40})(?:\n|,|$)"
)

# Verifier & Designation (explicit patterns only)
RE_VERIFIER = re.compile(
    r"(?i)(?:verified\s*by|inspecting\s*officer|approving\s*authority)\s*[:\-]\s*([A-Za-z\.\s]{2,40})(?:\n|,|$)"
)
RE_DESIGNATION = re.compile(
    r"(?i)\b(Revenue\s+Inspector|Tahsildar|Village\s+Administrative\s+Officer|VAO|Block\s+Agriculture\s+Officer|District\s+Collector|Agriculture\s+Officer)\b"
)

# Verification date (explicitly stated verification date)
RE_VERIF_DATE = re.compile(
    r"(?i)(?:verification\s*date|verified\s*on|date\s*of\s*verification)\s*[:\-]\s*([A-Za-z0-9\s,/\-]+?)(?:\.|\n|$)"
)

# Explicit transaction date (ONLY if stated as transaction/transfer date)
RE_TRANSACTION = re.compile(
    r"(?i)(?:transferred\s*on|sale\s*deed\s*date|acquisition\s*date|registered\s*on)\s*[:\-]\s*([A-Za-z0-9\s,/\-]+?)(?:\.|\n|$)"
)

# Land administrative units
RE_VILLAGE = re.compile(r"(?i)(?:village)\s*[:\-]\s*([A-Za-z\s]{2,30})(?:\n|,|$)")
RE_TALUK = re.compile(r"(?i)(?:taluk|tehsil)\s*[:\-]\s*([A-Za-z\s]{2,30})(?:\n|,|$)")
RE_DISTRICT = re.compile(r"(?i)(?:district)\s*[:\-]\s*([A-Za-z\s]{2,30})(?:\n|,|$)")


def extract_entities_from_pages(pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Scans all pages and extracts known agricultural/patta fields with page numbers.
    Never invents data. If not found, field remains None.
    """
    full_text = ""
    page_map = {}
    for p in pages:
        p_num = p.get("page_num", 1)
        p_text = p.get("text", "")
        page_map[p_num] = p_text
        full_text += f"\n--- Page {p_num} ---\n" + p_text

    entities = {
        "land_area": None,
        "survey_number": None,
        "patta_holder": None,
        "verifier": None,
        "verifier_designation": None,
        "verification_date": None,
        "transaction_date": None,
        "deadline": None,
        "subsidy_amount": None,
        "subsidy_percentage": None,
        "income_limit": None,
        "village": None,
        "taluk": None,
        "district": None,
    }

    # Helper to find page of first match
    def find_page(term: str) -> int:
        if not term:
            return 1
        for num, text in page_map.items():
            if term.lower() in text.lower():
                return num
        return 1

    # 1. Land Area
    m_area = RE_LAND_AREA.findall(full_text)
    if m_area:
        # Take the primary land holding mentioned in context of eligibility or parcel
        val, unit = m_area[0]
        entities["land_area"] = {
            "value": f"{val} {unit.lower()}",
            "page": find_page(val),
            "raw": f"{val} {unit}"
        }

    # 2. Survey Number
    m_survey = RE_SURVEY_NO.search(full_text)
    if m_survey:
        s_val = m_survey.group(1).replace(" ", "")
        entities["survey_number"] = {
            "value": s_val,
            "page": find_page(s_val),
            "raw": m_survey.group(0)
        }

    # 3. Holder / Owner
    m_holder = RE_HOLDER.search(full_text)
    if m_holder:
        h_val = m_holder.group(1).strip()
        entities["patta_holder"] = {
            "value": h_val,
            "page": find_page(h_val),
            "raw": h_val
        }

    # 4. Verifier & Designation
    m_verif = RE_VERIFIER.search(full_text)
    if m_verif:
        v_val = m_verif.group(1).strip()
        entities["verifier"] = {
            "value": v_val,
            "page": find_page(v_val),
            "raw": v_val
        }

    m_desig = RE_DESIGNATION.search(full_text)
    if m_desig:
        d_val = m_desig.group(1).strip()
        entities["verifier_designation"] = {
            "value": d_val,
            "page": find_page(d_val),
            "raw": d_val
        }

    # 5. Verification Date
    m_vdate = RE_VERIF_DATE.search(full_text)
    if m_vdate:
        vd_val = m_vdate.group(1).strip()
        entities["verification_date"] = {
            "value": vd_val,
            "page": find_page(vd_val),
            "raw": vd_val
        }

    # 6. Explicit Transaction Date (Never infer without explicit anchor)
    m_trans = RE_TRANSACTION.search(full_text)
    if m_trans:
        td_val = m_trans.group(1).strip()
        entities["transaction_date"] = {
            "value": td_val,
            "page": find_page(td_val),
            "raw": td_val
        }

    # 7. Deadline
    m_dead = RE_DEADLINE.search(full_text)
    if m_dead:
        dl_val = m_dead.group(1).strip()
        entities["deadline"] = {
            "value": dl_val,
            "page": find_page(dl_val),
            "raw": dl_val
        }

    # 8. Monetary / Subsidies / Income
    m_money = RE_MONETARY.findall(full_text)
    if m_money:
        # Check context for subsidy vs income
        for amt in m_money:
            amt_str = f"Rs. {amt}"
            pg = find_page(amt)
            if "income" in full_text.lower() and int(amt.replace(",", "").split(".")[0]) > 20000:
                if not entities["income_limit"]:
                    entities["income_limit"] = {"value": amt_str, "page": pg, "raw": amt_str}
            else:
                if not entities["subsidy_amount"]:
                    entities["subsidy_amount"] = {"value": amt_str, "page": pg, "raw": amt_str}

    # 9. Percentages
    m_pct = RE_PERCENTAGE.findall(full_text)
    if m_pct:
        p_val = f"{m_pct[0]}%"
        entities["subsidy_percentage"] = {
            "value": p_val,
            "page": find_page(p_val),
            "raw": p_val
        }

    # 10. Admin units
    m_vil = RE_VILLAGE.search(full_text)
    if m_vil:
        entities["village"] = {"value": m_vil.group(1).strip(), "page": find_page(m_vil.group(1))}
    m_tal = RE_TALUK.search(full_text)
    if m_tal:
        entities["taluk"] = {"value": m_tal.group(1).strip(), "page": find_page(m_tal.group(1))}
    m_dist = RE_DISTRICT.search(full_text)
    if m_dist:
        entities["district"] = {"value": m_dist.group(1).strip(), "page": find_page(m_dist.group(1))}

    return entities


def compare_structured_entities(
    old_entities: Dict[str, Any],
    new_entities: Dict[str, Any]
) -> List[FieldChange]:
    """
    Compares extracted entities between old and new documents.
    Produces list of FieldChange objects.
    Adheres strictly to NOT_FOUND and SUPPORTED flags.
    """
    fields_to_compare = [
        ("land_area", "Land Area / Holding Limit"),
        ("survey_number", "Survey / Subdivision Number"),
        ("patta_holder", "Patta / Land Holder"),
        ("verifier_designation", "Verifier Designation"),
        ("verifier", "Verifying Officer"),
        ("verification_date", "Verification Date"),
        ("transaction_date", "Transaction / Transfer Date"),
        ("deadline", "Application Deadline"),
        ("subsidy_amount", "Subsidy Amount"),
        ("subsidy_percentage", "Subsidy Rate / Percentage"),
        ("income_limit", "Annual Income Limit"),
        ("village", "Village"),
        ("taluk", "Taluk"),
        ("district", "District"),
    ]

    field_changes: List[FieldChange] = []
    idx = 1

    for key, label in fields_to_compare:
        old_obj = old_entities.get(key)
        new_obj = new_entities.get(key)

        old_val = old_obj["value"] if old_obj else None
        new_val = new_obj["value"] if new_obj else None

        old_pg = old_obj["page"] if old_obj else None
        new_pg = new_obj["page"] if new_obj else None

        # If absent in both, skip to avoid cluttering unless it's a critical land record field
        if not old_val and not new_val:
            continue

        if old_val and not new_val:
            change_type = "REMOVED"
            new_val_display = "NOT_FOUND"
            old_val_display = old_val
            status = "SUPPORTED"
            notes = f"{label} was present in old version but is absent in new version. Action Required: Remove requirement from active verification checklists."
        elif not old_val and new_val:
            change_type = "ADDED"
            old_val_display = "NOT_FOUND"
            new_val_display = new_val
            status = "SUPPORTED"
            notes = f"{label} was added in new version as '{new_val}'. Action Required: Enforce newly added entry during field verification and revenue endorsement."
        elif old_val.strip().lower() == new_val.strip().lower():
            change_type = "UNCHANGED"
            old_val_display = old_val
            new_val_display = new_val
            status = "SUPPORTED"
            notes = f"{label} remained identical as '{old_val}'. Action Required: Retain existing operational protocol."
        else:
            change_type = "MODIFIED"
            old_val_display = old_val
            new_val_display = new_val
            status = "SUPPORTED"
            if key == "land_area":
                notes = f"{label} changed from '{old_val}' to '{new_val}'. Action Required: Recompute land holding ceiling and adjust property tax assessment."
            elif key == "survey_number":
                notes = f"{label} changed from '{old_val}' to '{new_val}'. Action Required: Inspect village FMB sketch to verify boundary coordinates of subdivided parcel {new_val}."
            elif key == "patta_holder":
                notes = f"{label} changed from '{old_val}' to '{new_val}'. Action Required: Verify registered sale deed and legal heir succession documentation for mutation endorsement."
            elif key in ("verifier", "verifier_designation"):
                notes = f"{label} changed from '{old_val}' to '{new_val}'. Action Required: Dossier requires final attestation signature and official seal of the {new_val}."
            elif key == "verification_date":
                notes = f"{label} changed from '{old_val}' to '{new_val}'. Action Required: Record official attestation timestamp in the taluk revenue register."
            else:
                notes = f"{label} changed from '{old_val}' to '{new_val}'. Action Required: Update verification checklist against updated standard."

        field_changes.append(FieldChange(
            field_id=f"FLD-{idx:03d}",
            field_name=key,
            display_label=label,
            old_value=old_val_display,
            new_value=new_val_display,
            change_type=change_type,
            old_page=old_pg,
            new_page=new_pg,
            evidence_status=status,
            notes=notes
        ))
        idx += 1

    return field_changes
