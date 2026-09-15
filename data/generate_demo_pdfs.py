"""
AgriDiff AI — Demo PDF Generator
Creates the two controlled demo PDFs for the hackathon demo.
Run this ONCE to generate demo_old_policy.pdf and demo_new_policy.pdf.

Usage:
    pip install reportlab
    python generate_demo_pdfs.py
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.colors import HexColor
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT_DIR, exist_ok=True)

GREEN = HexColor("#166534")
GRAY  = HexColor("#6b7280")

styles = getSampleStyleSheet()

TITLE_STYLE = ParagraphStyle(
    "Title", parent=styles["Heading1"],
    fontSize=16, textColor=GREEN, spaceAfter=8,
)
SECTION_STYLE = ParagraphStyle(
    "Section", parent=styles["Heading2"],
    fontSize=12, textColor=GREEN, spaceBefore=14, spaceAfter=4,
)
BODY_STYLE = ParagraphStyle(
    "Body", parent=styles["Normal"],
    fontSize=10, leading=16, spaceAfter=4,
)
FOOTER_STYLE = ParagraphStyle(
    "Footer", parent=styles["Normal"],
    fontSize=8, textColor=GRAY, alignment=1,
)


def build_doc(filename: str, title: str, content: list):
    path = os.path.join(OUT_DIR, filename)
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    story = [Paragraph(title, TITLE_STYLE), HRFlowable(width="100%", thickness=1, color=GREEN), Spacer(1, 0.3*cm)]
    for item in content:
        if item.startswith("##"):
            story.append(Paragraph(item[2:].strip(), SECTION_STYLE))
        elif item == "---":
            story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY))
            story.append(Spacer(1, 0.2*cm))
        else:
            story.append(Paragraph(item, BODY_STYLE))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("CODEAVENGERS | BIT-AI-001 | AGR-17 | AgriDiff AI Demo Document", FOOTER_STYLE))
    doc.build(story)
    print(f"[OK] Created: {path}")


# ── Old Policy (2023) ──────────────────────────────────────────────────────────
OLD_CONTENT = [
    "## 1. ELIGIBILITY CRITERIA",
    "Farmers owning land up to 2 hectares shall be eligible for this scheme.",
    "Annual income of the farmer must not exceed Rs. 1,50,000 per year.",
    "Only permanent residents of the State are eligible to apply.",
    "---",
    "## 2. FINANCIAL ASSISTANCE",
    "Eligible farmers shall receive a subsidy of Rs. 5,000 per season.",
    "Maximum assistance per farmer per year shall not exceed Rs. 10,000.",
    "The subsidy shall be credited directly to the farmer's bank account.",
    "---",
    "## 3. APPLICATION DEADLINE",
    "Applications must be submitted by 31st March of each year.",
    "Applications received after the deadline shall not be considered.",
    "---",
    "## 4. REQUIRED DOCUMENTS",
    "The following documents must be submitted along with the application:",
    "a) Aadhaar Card (self-attested copy)",
    "b) Land Records (Khatauni / Patta)",
    "c) Bank Passbook (showing account details)",
    "---",
    "## 5. PROCEDURE",
    "Farmers must visit the nearest Krishi Vigyan Kendra (KVK) to register.",
    "Verification by the Block Agriculture Officer shall be completed within 30 days.",
    "Approved applications shall be processed by the State Agriculture Department.",
    "---",
    "## 6. BENEFICIARY CONDITIONS",
    "The scheme is applicable only to individual farmers.",
    "Cooperative farming societies are not covered under this scheme.",
    "A farmer may avail the scheme only once per financial year.",
]

# ── New Policy (2024) ──────────────────────────────────────────────────────────
NEW_CONTENT = [
    "## 1. ELIGIBILITY CRITERIA",
    "Farmers owning land up to 5 hectares shall be eligible for this scheme.",
    "Annual income of the farmer must not exceed Rs. 2,00,000 per year.",
    "Only permanent residents of the State are eligible to apply.",
    "---",
    "## 2. FINANCIAL ASSISTANCE",
    "Eligible farmers shall receive a subsidy of Rs. 8,000 per season.",
    "Maximum assistance per farmer per year shall not exceed Rs. 16,000.",
    "The subsidy shall be credited directly to the farmer's bank account.",
    "---",
    "## 3. APPLICATION DEADLINE",
    "Applications must be submitted by 30th June of each year.",
    "Applications received after the deadline shall not be considered.",
    "---",
    "## 4. REQUIRED DOCUMENTS",
    "The following documents must be submitted along with the application:",
    "a) Aadhaar Card (self-attested copy)",
    "b) Land Records (Khatauni / Patta)",
    "c) Bank Passbook (showing account details)",
    "d) Caste Certificate (mandatory for SC/ST category farmers)",
    "---",
    "## 5. PROCEDURE",
    "Farmers may register online at agri.state.gov.in OR visit the nearest Krishi Vigyan Kendra (KVK).",
    "Verification by the Block Agriculture Officer shall be completed within 15 days.",
    "Approved applications shall be processed by the State Agriculture Department.",
    "---",
    "## 6. BENEFICIARY CONDITIONS",
    "The scheme is applicable to individual farmers and registered Farmer Producer Organizations (FPOs).",
    "Cooperative farming societies are not covered under this scheme.",
    "A farmer may avail the scheme only once per financial year.",
    "---",
    "## 7. GRIEVANCE REDRESSAL",
    "Farmers may submit grievances through the State Agriculture Portal (agri.state.gov.in).",
    "All grievances must be submitted within 60 days of the rejection notice.",
    "The Grievance Redressal Officer shall respond within 21 working days.",
]


if __name__ == "__main__":
    build_doc(
        "demo_old_policy.pdf",
        "Agricultural Support Scheme Guidelines 2023",
        OLD_CONTENT,
    )
    build_doc(
        "demo_new_policy.pdf",
        "Agricultural Support Scheme Guidelines 2024",
        NEW_CONTENT,
    )
    print("\nDemo PDFs ready in data/ folder.")
    print("   Use these for the hackathon demo -- 9 ground-truth changes included.")
