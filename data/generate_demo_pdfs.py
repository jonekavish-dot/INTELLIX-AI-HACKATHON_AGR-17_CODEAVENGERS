"""
AgriDiff AI — Demo Document & Ground Truth Generator
Generates:
1. Comprehensive Agricultural Policy Pair with 22 controlled changes (T01-T20 coverage)
2. Synthetic Patta / Land Record Pair (survey numbers, land areas, holders, verifiers)
3. Synchronized ground_truth.json with exact 22 labeled changes

BIT-AI-001 | AGR-17 | Team CODEAVENGERS
"""

import os
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.colors import HexColor

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT_DIR, exist_ok=True)

GREEN = HexColor("#166534")
GRAY = HexColor("#6b7280")

styles = getSampleStyleSheet()

TITLE_STYLE = ParagraphStyle(
    "Title", parent=styles["Heading1"],
    fontSize=15, textColor=GREEN, spaceAfter=6, fontName="Helvetica-Bold"
)
SECTION_STYLE = ParagraphStyle(
    "Section", parent=styles["Heading2"],
    fontSize=11, textColor=GREEN, spaceBefore=10, spaceAfter=3, fontName="Helvetica-Bold"
)
BODY_STYLE = ParagraphStyle(
    "Body", parent=styles["Normal"],
    fontSize=9, leading=14, spaceAfter=3, fontName="Helvetica"
)
FOOTER_STYLE = ParagraphStyle(
    "Footer", parent=styles["Normal"],
    fontSize=8, textColor=GRAY, alignment=1, fontName="Helvetica"
)


def build_doc(filename: str, title: str, content: list):
    path = os.path.join(OUT_DIR, filename)
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        rightMargin=1.8*cm, leftMargin=1.8*cm,
        topMargin=1.8*cm, bottomMargin=1.8*cm,
    )
    story = [
        Paragraph(title, TITLE_STYLE),
        HRFlowable(width="100%", thickness=1.5, color=GREEN),
        Spacer(1, 0.2*cm)
    ]
    for item in content:
        if item.startswith("##"):
            story.append(Paragraph(item[2:].strip(), SECTION_STYLE))
        elif item == "---":
            story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY))
            story.append(Spacer(1, 0.15*cm))
        else:
            story.append(Paragraph(item, BODY_STYLE))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("BIT-AI-001 | AGR-17 | Team CODEAVENGERS — Synthetic Benchmark Document", FOOTER_STYLE))
    doc.build(story)
    print(f"[OK] Created: {path}")


# ─────────────────────────────────────────────────────────────────────────────
# 1. 22-CHANGE AGRICULTURAL POLICY PAIR (Old 2023 vs New 2024)
# ─────────────────────────────────────────────────────────────────────────────

OLD_POLICY_CONTENT = [
    "## 1. ELIGIBILITY CRITERIA",
    "1.1 Land Holding: Farmers owning agricultural land up to 2 hectares shall be eligible for the scheme.",
    "1.2 Annual Income: The total annual family income of the applicant must not exceed Rs. 1,50,000.",
    "1.3 Domicile: The farmer must be a permanent resident of the State holding a valid Domicile Certificate.",
    "1.4 Age Limit: Applicants must be between 18 and 65 years of age on the date of application.",
    "---",
    "## 2. FINANCIAL ASSISTANCE & SUBSIDY",
    "2.1 Seasonal Subsidy: Eligible small and marginal farmers shall receive a direct cash subsidy of Rs. 5,000 per cropping season.",
    "2.2 Annual Maximum: The total maximum financial assistance per farmer household shall not exceed Rs. 10,000 per financial year.",
    "2.3 Subsidy Rate: Solar water pump installation assistance is fixed at 40% of the benchmark equipment cost.",
    "2.4 Disbursement: Subsidy disbursements shall be credited directly via Direct Benefit Transfer (DBT) to the farmer's Aadhaar-linked savings bank account.",
    "---",
    "## 3. APPLICATION DEADLINE & TIMELINE",
    "3.1 Submission Cut-off: Complete applications for Kharif season must be submitted on or before 30-09-2026.",
    "3.2 Scrutiny Period: Initial scrutiny by the Village Agriculture Officer shall be concluded within 30 days of submission.",
    "---",
    "## 4. DOCUMENTATION REQUIREMENTS",
    "4.1 Mandatory Documents: Applicants must submit self-attested copies of:",
    "a) Aadhaar Card for identification",
    "b) Land Ownership Record (Khatauni / Chitta)",
    "c) Bank Passbook with active IFSC details",
    "4.2 Physical Verification: Physical submission of physical hard copies is mandatory at the local Agricultural Extension Center.",
    "---",
    "## 5. BENEFICIARY COVERAGE",
    "5.1 Individual Farmers: The scheme applies strictly to individual farmer landholders.",
    "5.2 Excluded Categories: Institutional landholders, corporate farming entities, and government employees are barred from claiming benefits.",
    "5.3 Frequency: An eligible farmer may avail of the scheme only once per agricultural cycle.",
    "---",
    "## 6. ADMINISTRATIVE PROCEDURE",
    "6.1 Registration: Registration shall be performed in-person by visiting the nearest Krishi Vigyan Kendra (KVK).",
    "6.2 Approval Authority: The approving officer for financial sanction is the Block Agriculture Officer.",
    "---",
    "## 7. MONITORING & AUDIT",
    "7.1 Post-Disbursement Inspection: 5% of all beneficiary farms shall be randomly inspected post-harvest.",
    "7.2 Utilization Certificate: Beneficiaries must submit a simple signed utilization voucher within 90 days."
]

NEW_POLICY_CONTENT = [
    "## 1. ELIGIBILITY CRITERIA",
    # CH-001: Land area 2 ha -> 5 ha (MODIFIED / HIGH)
    "1.1 Land Holding: Farmers owning agricultural land up to 5 hectares shall be eligible for the scheme.",
    # CH-002: Income limit Rs. 1,50,000 -> Rs. 2,00,000 (MODIFIED / MEDIUM)
    "1.2 Annual Income: The total annual family income of the applicant must not exceed Rs. 2,00,000.",
    # CH-003: Domicile (SEMANTICALLY_EQUIVALENT - reworded, same meaning)
    "1.3 Domicile: The scheme is restricted to permanent state inhabitants who produce authenticated domicile verification.",
    # CH-004: Age Limit 65 -> 70 (MODIFIED / LOW)
    "1.4 Age Limit: Applicants must be between 18 and 70 years of age on the date of application.",
    # CH-005: New Tenant Farmer clause added (ADDED / HIGH)
    "1.5 Tenant Farmers: Registered tenant cultivators with valid lease agreements for at least 3 years are now eligible.",
    "---",
    "## 2. FINANCIAL ASSISTANCE & SUBSIDY",
    # CH-006: Subsidy Rs. 5,000 -> Rs. 8,000 (MODIFIED / HIGH)
    "2.1 Seasonal Subsidy: Eligible small and marginal farmers shall receive a direct cash subsidy of Rs. 8,000 per cropping season.",
    # CH-007: Annual max Rs. 10,000 -> Rs. 16,000 (MODIFIED / HIGH)
    "2.2 Annual Maximum: The total maximum financial assistance per farmer household shall not exceed Rs. 16,000 per financial year.",
    # CH-008: Subsidy rate 40% -> 50% (MODIFIED / HIGH)
    "2.3 Subsidy Rate: Solar water pump installation assistance is fixed at 50% of the benchmark equipment cost.",
    # CH-009: Additional organic bonus added (ADDED / MEDIUM)
    "2.4 Organic Farming Bonus: An additional incentive grant of Rs. 3,000 per hectare is provided for certified organic farming plots.",
    # CH-010: Disbursement method identical (UNCHANGED)
    "2.5 Disbursement: Subsidy disbursements shall be credited directly via Direct Benefit Transfer (DBT) to the farmer's Aadhaar-linked savings bank account.",
    "---",
    "## 3. APPLICATION DEADLINE & TIMELINE",
    # CH-011: Deadline extended 30-09-2026 -> 15-10-2026 (MODIFIED / HIGH)
    "3.1 Submission Cut-off: Complete applications for Kharif season must be submitted on or before 15-10-2026.",
    # CH-012: Scrutiny period reduced 30 -> 15 days (MODIFIED / MEDIUM)
    "3.2 Scrutiny Period: Initial scrutiny by the Village Agriculture Officer shall be concluded within 15 days of submission.",
    # CH-013: Late application fee clause added (ADDED / LOW)
    "3.3 Grace Period: Late submissions are accepted up to 7 days post-deadline subject to a Rs. 100 processing surcharge.",
    "---",
    "## 4. DOCUMENTATION REQUIREMENTS",
    "4.1 Mandatory Documents: Applicants must submit self-attested copies of:",
    "a) Aadhaar Card for identification",
    "b) Land Ownership Record (Khatauni / Chitta)",
    "c) Bank Passbook with active IFSC details",
    # CH-014: Soil Health Card added (ADDED / MEDIUM)
    "d) Soil Health Card issued within the past 2 years",
    # CH-015: Caste Certificate added for SC/ST (ADDED / MEDIUM)
    "e) Caste Certificate (mandatory for SC/ST applicants claiming special sub-allocation)",
    # CH-016: Physical verification replaced with online upload (MODIFIED / MEDIUM)
    "4.2 Online Upload: Physical submission is discontinued; all documents must be scanned and uploaded directly on the State Agriculture Portal.",
    "---",
    "## 5. BENEFICIARY COVERAGE",
    # CH-017: Extended to FPOs (MODIFIED / HIGH)
    "5.1 Beneficiary Scope: The scheme applies to individual farmer landholders and registered Farmer Producer Organizations (FPOs).",
    # CH-018: Excluded categories unchanged (UNCHANGED)
    "5.2 Excluded Categories: Institutional landholders, corporate farming entities, and government employees are barred from claiming benefits.",
    # (Old clause 5.3 Frequency restriction has been completely REMOVED -> CH-019 / REMOVED / HIGH)
    "---",
    "## 6. ADMINISTRATIVE PROCEDURE",
    # CH-020: Online registration added alongside KVK (MODIFIED / MEDIUM)
    "6.1 Registration: Registration can be performed online at agri.state.gov.in or in-person at the nearest Krishi Vigyan Kendra (KVK).",
    # CH-021: Approving authority upgraded to Assistant Director of Agriculture (MODIFIED / MEDIUM)
    "6.2 Approval Authority: The approving officer for financial sanction is the Assistant Director of Agriculture.",
    "---",
    # (Old Section 7 Monitoring has been simplified; 7.1 Random inspection REMOVED -> CH-022 / REMOVED / MEDIUM)
    "## 7. MONITORING & GRIEVANCE REDRESSAL",
    "7.1 Grievance Redressal Portal: Any grievance regarding non-receipt of subsidy must be logged within 45 days at agri.state.gov.in/grievance."
]


# ─────────────────────────────────────────────────────────────────────────────
# 2. SYNTHETIC PATTA / LAND RECORD PAIR
# ─────────────────────────────────────────────────────────────────────────────

OLD_LAND_RECORD = [
    "## GOVERNMENT REVENUE ADMINISTRATION — PATTA & LAND RECORD",
    "District: Coimbatore | Taluk: Pollachi | Village: Anaimalai",
    "Document Number: PATTA-2023-REV-8841",
    "---",
    "## 1. LAND IDENTIFICATION",
    "Survey Number: 123",
    "Subdivision: 1A",
    "Land Area: 2 acres",
    "Soil Classification: Dry Land (Punja)",
    "---",
    "## 2. RECORDED HOLDER",
    "Patta Holder: ABC",
    "Father / Guardian: Ramanathan",
    "Holding Status: Individual Title",
    "---",
    "## 3. ADMINISTRATIVE VERIFICATION",
    "Verified By: Revenue Inspector",
    "Designation: Revenue Inspector",
    "Verification Date: NOT_STATED",
    "---",
    "## 4. REMARKS & RECORD NOTES",
    "Registered agricultural land free of encumbrance as per 2023 village survey register."
]

NEW_LAND_RECORD = [
    "## GOVERNMENT REVENUE ADMINISTRATION — PATTA & LAND RECORD",
    "District: Coimbatore | Taluk: Pollachi | Village: Anaimalai",
    "Document Number: PATTA-2024-REV-9104",
    "---",
    "## 1. LAND IDENTIFICATION",
    # Survey Number changed: 123 -> 123/2
    "Survey Number: 123/2",
    "Subdivision: 2B",
    # Land Area changed: 2 acres -> 4 acres (added parcel)
    "Land Area: 4 acres",
    "Soil Classification: Dry Land (Punja)",
    "---",
    "## 2. RECORDED HOLDER",
    # Holder changed: ABC -> XYZ
    "Patta Holder: XYZ",
    "Father / Guardian: Ramanathan",
    "Holding Status: Individual Title",
    "---",
    "## 3. ADMINISTRATIVE VERIFICATION",
    # Verifier changed: Revenue Inspector -> Tahsildar
    "Verified By: Tahsildar",
    "Designation: Tahsildar",
    # Verification date explicitly added
    "Verification Date: 15-10-2026",
    # Explicit transaction note
    "Transaction Date: 10-09-2026",
    "---",
    "## 4. REMARKS & RECORD NOTES",
    "Subdivided land parcel updated with additional 2 acres consolidation approved by Revenue Divisional Officer."
]


# ─────────────────────────────────────────────────────────────────────────────
# 3. 22-CHANGE GROUND TRUTH DATASET
# ─────────────────────────────────────────────────────────────────────────────

GROUND_TRUTH_DATA = {
    "dataset": "AgriDiff AI Benchmark 2026 (AGR-17)",
    "total_changes": 22,
    "description": "Comprehensive controlled benchmark dataset with 22 ground truth changes covering all T01-T20 test requirements.",
    "changes": [
        {
            "id": "GT-001",
            "section": "ELIGIBILITY CRITERIA",
            "category": "Eligibility",
            "field": "land_area",
            "change_type": "MODIFIED",
            "impact": "HIGH",
            "old_value": "2 hectares",
            "new_value": "5 hectares",
            "description": "Land holding limit expanded from 2 hectares to 5 hectares"
        },
        {
            "id": "GT-002",
            "section": "ELIGIBILITY CRITERIA",
            "category": "Eligibility",
            "field": "income_limit",
            "change_type": "MODIFIED",
            "impact": "MEDIUM",
            "old_value": "Rs. 1,50,000",
            "new_value": "Rs. 2,00,000",
            "description": "Annual income ceiling increased from Rs. 1,50,000 to Rs. 2,00,000"
        },
        {
            "id": "GT-003",
            "section": "ELIGIBILITY CRITERIA",
            "category": "Eligibility",
            "field": "domicile",
            "change_type": "SEMANTICALLY_EQUIVALENT",
            "impact": "LOW",
            "old_value": None,
            "new_value": None,
            "description": "Domicile condition reworded with identical legal requirement"
        },
        {
            "id": "GT-004",
            "section": "ELIGIBILITY CRITERIA",
            "category": "Eligibility",
            "field": "age_limit",
            "change_type": "MODIFIED",
            "impact": "LOW",
            "old_value": "65 years",
            "new_value": "70 years",
            "description": "Maximum age limit raised from 65 to 70 years"
        },
        {
            "id": "GT-005",
            "section": "ELIGIBILITY CRITERIA",
            "category": "Eligibility",
            "field": "tenant_farmers",
            "change_type": "ADDED",
            "impact": "HIGH",
            "old_value": None,
            "new_value": "Registered tenant cultivators (3-year lease)",
            "description": "New clause making tenant farmers eligible"
        },
        {
            "id": "GT-006",
            "section": "FINANCIAL ASSISTANCE & SUBSIDY",
            "category": "Financial",
            "field": "subsidy_amount",
            "change_type": "MODIFIED",
            "impact": "HIGH",
            "old_value": "Rs. 5,000",
            "new_value": "Rs. 8,000",
            "description": "Seasonal cash subsidy raised from Rs. 5,000 to Rs. 8,000"
        },
        {
            "id": "GT-007",
            "section": "FINANCIAL ASSISTANCE & SUBSIDY",
            "category": "Financial",
            "field": "annual_max_subsidy",
            "change_type": "MODIFIED",
            "impact": "HIGH",
            "old_value": "Rs. 10,000",
            "new_value": "Rs. 16,000",
            "description": "Annual assistance ceiling raised from Rs. 10,000 to Rs. 16,000"
        },
        {
            "id": "GT-008",
            "section": "FINANCIAL ASSISTANCE & SUBSIDY",
            "category": "Financial",
            "field": "subsidy_percentage",
            "change_type": "MODIFIED",
            "impact": "HIGH",
            "old_value": "40%",
            "new_value": "50%",
            "description": "Solar pump subsidy rate increased from 40% to 50%"
        },
        {
            "id": "GT-009",
            "section": "FINANCIAL ASSISTANCE & SUBSIDY",
            "category": "Financial",
            "field": "organic_farming_bonus",
            "change_type": "ADDED",
            "impact": "MEDIUM",
            "old_value": None,
            "new_value": "Rs. 3,000 per hectare",
            "description": "Added organic farming bonus grant of Rs. 3,000/ha"
        },
        {
            "id": "GT-010",
            "section": "FINANCIAL ASSISTANCE & SUBSIDY",
            "category": "Financial",
            "field": "disbursement_mode",
            "change_type": "UNCHANGED",
            "impact": "LOW",
            "old_value": "DBT Aadhaar-linked",
            "new_value": "DBT Aadhaar-linked",
            "description": "Direct Benefit Transfer provision remained unchanged"
        },
        {
            "id": "GT-011",
            "section": "APPLICATION DEADLINE & TIMELINE",
            "category": "Deadline",
            "field": "deadline",
            "change_type": "MODIFIED",
            "impact": "HIGH",
            "old_value": "30-09-2026",
            "new_value": "15-10-2026",
            "description": "Submission deadline extended from 30-09-2026 to 15-10-2026"
        },
        {
            "id": "GT-012",
            "section": "APPLICATION DEADLINE & TIMELINE",
            "category": "Procedure",
            "field": "scrutiny_period",
            "change_type": "MODIFIED",
            "impact": "MEDIUM",
            "old_value": "30 days",
            "new_value": "15 days",
            "description": "Application scrutiny period reduced from 30 days to 15 days"
        },
        {
            "id": "GT-013",
            "section": "APPLICATION DEADLINE & TIMELINE",
            "category": "Deadline",
            "field": "grace_period",
            "change_type": "ADDED",
            "impact": "LOW",
            "old_value": None,
            "new_value": "7 days with Rs. 100 surcharge",
            "description": "7-day grace period with Rs. 100 fee added"
        },
        {
            "id": "GT-014",
            "section": "DOCUMENTATION REQUIREMENTS",
            "category": "Documentation",
            "field": "soil_health_card",
            "change_type": "ADDED",
            "impact": "MEDIUM",
            "old_value": None,
            "new_value": "Soil Health Card (past 2 years)",
            "description": "Soil Health Card added as required document"
        },
        {
            "id": "GT-015",
            "section": "DOCUMENTATION REQUIREMENTS",
            "category": "Documentation",
            "field": "caste_certificate",
            "change_type": "ADDED",
            "impact": "MEDIUM",
            "old_value": None,
            "new_value": "Caste Certificate (for SC/ST)",
            "description": "Caste Certificate added for SC/ST applicants"
        },
        {
            "id": "GT-016",
            "section": "DOCUMENTATION REQUIREMENTS",
            "category": "Procedure",
            "field": "submission_mode",
            "change_type": "MODIFIED",
            "impact": "MEDIUM",
            "old_value": "Physical submission at Extension Center",
            "new_value": "Online portal scan upload",
            "description": "Physical hard-copy submission replaced by online scanned upload"
        },
        {
            "id": "GT-017",
            "section": "BENEFICIARY COVERAGE",
            "category": "Beneficiary",
            "field": "fpo_coverage",
            "change_type": "MODIFIED",
            "impact": "HIGH",
            "old_value": "Individual farmers only",
            "new_value": "Individual farmers and registered FPOs",
            "description": "Scheme scope extended to Farmer Producer Organizations (FPOs)"
        },
        {
            "id": "GT-018",
            "section": "BENEFICIARY COVERAGE",
            "category": "Beneficiary",
            "field": "exclusions",
            "change_type": "UNCHANGED",
            "impact": "LOW",
            "old_value": "Institutional landholders excluded",
            "new_value": "Institutional landholders excluded",
            "description": "Corporate / institutional exclusion remained intact"
        },
        {
            "id": "GT-019",
            "section": "BENEFICIARY COVERAGE",
            "category": "Beneficiary",
            "field": "frequency_limit",
            "change_type": "REMOVED",
            "impact": "HIGH",
            "old_value": "Once per agricultural cycle",
            "new_value": None,
            "description": "One-claim-per-cycle restriction removed, allowing multi-crop claims"
        },
        {
            "id": "GT-020",
            "section": "ADMINISTRATIVE PROCEDURE",
            "category": "Procedure",
            "field": "registration_mode",
            "change_type": "MODIFIED",
            "impact": "MEDIUM",
            "old_value": "In-person at KVK only",
            "new_value": "Online portal OR in-person at KVK",
            "description": "Online registration channel added alongside KVK"
        },
        {
            "id": "GT-021",
            "section": "ADMINISTRATIVE PROCEDURE",
            "category": "Procedure",
            "field": "approval_authority",
            "change_type": "MODIFIED",
            "impact": "MEDIUM",
            "old_value": "Block Agriculture Officer",
            "new_value": "Assistant Director of Agriculture",
            "description": "Approval authority elevated to Assistant Director of Agriculture"
        },
        {
            "id": "GT-022",
            "section": "MONITORING & GRIEVANCE REDRESSAL",
            "category": "Procedure",
            "field": "random_inspection",
            "change_type": "REMOVED",
            "impact": "MEDIUM",
            "old_value": "5% random post-harvest inspection",
            "new_value": None,
            "description": "Mandatory 5% post-harvest farm inspection clause removed"
        }
    ]
}


if __name__ == "__main__":
    print("Generating comprehensive agricultural documents...")
    # 1. 22-Change Policy Pair
    build_doc("demo_old_policy.pdf", "State Agricultural Development Scheme 2023", OLD_POLICY_CONTENT)
    build_doc("demo_new_policy.pdf", "State Agricultural Development Scheme 2024", NEW_POLICY_CONTENT)
    
    # 2. Patta & Land Record Pair
    build_doc("land_record_old.pdf", "Government Revenue Department — Patta Passbook 2023", OLD_LAND_RECORD)
    build_doc("land_record_new.pdf", "Government Revenue Department — Patta Passbook 2024", NEW_LAND_RECORD)

    # 3. Ground Truth JSON
    gt_path = os.path.join(OUT_DIR, "ground_truth.json")
    with open(gt_path, "w", encoding="utf-8") as f:
        json.dump(GROUND_TRUTH_DATA, f, indent=2)
    print(f"[OK] Created ground truth: {gt_path} with {len(GROUND_TRUTH_DATA['changes'])} verified changes.")
