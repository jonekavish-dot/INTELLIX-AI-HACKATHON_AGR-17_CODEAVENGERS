"""
AgriDiff AI — PDF Extractor
Extracts page-aware text from PDFs.
Primary: PyMuPDF | Fallback: pdfplumber | OCR: pytesseract
"""

import io
import logging
from typing import List, Dict

logger = logging.getLogger("agridiff.extractor")

OCR_THRESHOLD = 50  # chars/page — below this triggers OCR


def extract_pdf(file_bytes: bytes, filename: str) -> List[Dict]:
    """
    Extract text from a PDF, returning a list of page dicts.
    Each dict: { page_num, text, char_count, method }
    """
    pages = _extract_with_pymupdf(file_bytes, filename)

    # Check if text is sufficient or if OCR is needed
    avg_chars = sum(p["char_count"] for p in pages) / max(len(pages), 1)
    if avg_chars < OCR_THRESHOLD:
        logger.warning(f"[{filename}] Avg {avg_chars:.0f} chars/page — triggering OCR fallback")
        pages = _extract_with_ocr(file_bytes, filename)
    else:
        logger.info(f"[{filename}] Extracted {len(pages)} pages via PyMuPDF (avg {avg_chars:.0f} chars/page)")

    return pages


def _extract_with_pymupdf(file_bytes: bytes, filename: str) -> List[Dict]:
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = []
        for i, page in enumerate(doc):
            text = page.get_text("text").strip()
            pages.append({
                "page_num": i + 1,
                "text": text,
                "char_count": len(text),
                "method": "pymupdf",
            })
        doc.close()
        return pages
    except Exception as e:
        logger.warning(f"[{filename}] PyMuPDF failed: {e} — trying pdfplumber")
        return _extract_with_pdfplumber(file_bytes, filename)


def _extract_with_pdfplumber(file_bytes: bytes, filename: str) -> List[Dict]:
    try:
        import pdfplumber
        pages = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                text = (page.extract_text() or "").strip()
                pages.append({
                    "page_num": i + 1,
                    "text": text,
                    "char_count": len(text),
                    "method": "pdfplumber",
                })
        return pages
    except Exception as e:
        logger.error(f"[{filename}] pdfplumber also failed: {e}")
        return []


def _extract_with_ocr(file_bytes: bytes, filename: str) -> List[Dict]:
    """OCR fallback for scanned PDFs using pytesseract."""
    try:
        import fitz
        import pytesseract
        from PIL import Image
        import io as _io

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = []
        for i, page in enumerate(doc):
            mat = fitz.Matrix(2, 2)  # 2x scale for better OCR
            pix = page.get_pixmap(matrix=mat)
            img = Image.open(_io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img, lang="eng").strip()
            pages.append({
                "page_num": i + 1,
                "text": text,
                "char_count": len(text),
                "method": "ocr",
            })
        doc.close()
        logger.info(f"[{filename}] OCR complete — {len(pages)} pages")
        return pages
    except Exception as e:
        logger.error(f"[{filename}] OCR failed: {e}")
        return []

