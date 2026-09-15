"""
AgriDiff AI — Text Normalizer & Safe Deduplicator
Provides safe canonicalization of whitespace, line breaks, and punctuation
while strictly preserving numbers, dates, currency, percentages, units,
names, survey numbers, and negation terms.

BIT-AI-001 | AGR-17 | Team CODEAVENGERS
"""

import re
import unicodedata
from typing import Tuple, Dict, Any, List, Optional


# ── Critical Pattern Protections ───────────────────────────────────────────────

RE_NUMERIC_TOKENS = re.compile(
    r"\b(?:[0-9]{1,2}[/\-\.][0-9]{1,2}[/\-\.][0-9]{2,4}|[0-9]+/[0-9a-zA-Z]+|Rs\.?\s*[\d,]+|\d+\s*(?:acres?|hectares?|cents?|ha|sq\.?\s*m)|\d+\s*%|\d+(?:\.\d+)?)\b",
    re.IGNORECASE
)


RE_WHITESPACE = re.compile(r"\s+")
RE_LINEBREAKS = re.compile(r"[\r\n]+")
RE_PUNCTUATION = re.compile(r"[\.,;:!?\(\)\[\]\"'’“”\-—]+")


def normalize_whitespace(text: str) -> str:
    """Safely normalizes repeated whitespace and line breaks without losing tokens."""
    if not text:
        return ""
    # Normalize unicode
    t = unicodedata.normalize("NFKC", text)
    # Replace linebreaks with single spaces
    t = RE_LINEBREAKS.sub(" ", t)
    # Collapse multiple spaces into one
    t = RE_WHITESPACE.sub(" ", t)
    return t.strip()


def extract_critical_tokens(text: str) -> List[str]:
    """Extracts all numbers, currency, dates, percentages, and survey numbers."""
    if not text:
        return []
    clean = normalize_whitespace(text)
    return [m.lower().replace(" ", "") for m in RE_NUMERIC_TOKENS.findall(clean)]


def is_formatting_only_diff(text1: str, text2: str) -> bool:
    """
    Returns True if text1 and text2 differ ONLY in whitespace or punctuation,
    with identical alphanumeric and numeric content.
    """
    if text1 == text2:
        return True

    # 1. Check critical numeric tokens
    tokens1 = extract_critical_tokens(text1)
    tokens2 = extract_critical_tokens(text2)
    if tokens1 != tokens2:
        return False

    # 2. Compare alphanumeric words
    words1 = [w.lower() for w in re.findall(r"\b[A-Za-z0-9]+\b", text1)]
    words2 = [w.lower() for w in re.findall(r"\b[A-Za-z0-9]+\b", text2)]
    return words1 == words2


def extract_clause_identifier(text: str) -> Optional[str]:
    """
    Extracts clause or subclause identifier from the start of a text:
    e.g. '1.1 Land Holding' -> '1.1'
         '2.3 Subsidy Rate' -> '2.3'
         '4.2 Physical Verification' -> '4.2'
         'a) Aadhaar Card' -> 'a)'
    """
    if not text:
        return None
    # Subclause like 1.1, 2.3, 4.2.1
    m = re.match(r"^(\d+\.\d+(?:\.\d+)?)\b", text.strip())
    if m:
        return m.group(1)
    # Lettered list like a), b)
    m = re.match(r"^([a-z]\))\s*", text.strip(), re.IGNORECASE)
    if m:
        return m.group(1).lower()
    return None


def strip_clause_identifier(text: str) -> str:
    """
    Strips leading clause identifiers (e.g. '1.1 ', '2.4 ', 'a) ') from text
    to allow substantive comparison of body text.
    """
    if not text:
        return ""
    # Strip leading number pattern e.g. "1.1", "2.5.", "1."
    t = re.sub(r"^\d+(?:\.\d+)*\.?\s*", "", text.strip())
    # Strip leading list marker e.g. "a) ", "b) "
    t = re.sub(r"^[a-z]\)\s*", "", t, flags=re.IGNORECASE)
    return t.strip()



def deduplicate_evidence_spans(spans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicates overlapping or identical evidence spans."""
    seen = set()
    unique_spans = []
    for s in spans:
        key = (
            normalize_whitespace(s.get("old_text", "")),
            s.get("old_page"),
            normalize_whitespace(s.get("new_text", "")),
            s.get("new_page")
        )
        if key not in seen:
            seen.add(key)
            unique_spans.append(s)
    return unique_spans
