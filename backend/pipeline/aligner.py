"""
AgriDiff AI — Semantic Aligner
Maps old document chunks to new document chunks using cosine similarity.
Produces exhaustive pairs with semantic tagging.
BIT-AI-001 | AGR-17 | Team CODEAVENGERS
"""

import logging
import numpy as np
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("agridiff.aligner")

EQUIVALENT_THRESHOLD = 0.95   # >= this with small textual diff -> SEMANTICALLY_EQUIVALENT
REWORD_THRESHOLD = 0.85       # >= this -> REWORDED / structural change
MODIFIED_THRESHOLD = 0.35     # >= this -> MODIFIED match


import re
try:
    from pipeline.normalizer import (
        is_formatting_only_diff,
        extract_critical_tokens,
        strip_clause_identifier,
    )
except ImportError:
    from backend.pipeline.normalizer import (
        is_formatting_only_diff,
        extract_critical_tokens,
        strip_clause_identifier,
    )


def align_chunks(
    old_chunks: List[Dict],
    new_chunks: List[Dict],
    old_embeddings: np.ndarray,
    new_embeddings: np.ndarray,
) -> List[Dict]:
    """
    Align old chunks to new chunks using cosine similarity matrix and structural hints.
    Returns list of aligned pair dicts.
    Guarantees every chunk is represented (EXHAUSTIVE).
    """
    if len(old_chunks) == 0 or len(new_chunks) == 0:
        logger.warning("Empty chunk list received — fallback to all added/removed")
        return _all_as_added_or_removed(old_chunks, new_chunks)

    # Cosine similarity matrix: shape (len(old), len(new))
    sim_matrix = cosine_similarity(old_embeddings, new_embeddings)

    pairs = []
    used_new_indices = set()
    used_old_indices = set()

    # Pass 1: Structural pairing by clause identifier (e.g. 1.1, 4.2, a), etc.)
    # Pair if same subclause AND sim >= 0.25 (to avoid pairing completely unrelated clauses that reuse a number)
    for old_idx, old_chunk in enumerate(old_chunks):
        o_sub = old_chunk.get("section_number")
        if not o_sub:
            continue
        for new_idx, new_chunk in enumerate(new_chunks):
            if new_idx in used_new_indices:
                continue
            n_sub = new_chunk.get("section_number")
            if o_sub == n_sub:
                sim = float(sim_matrix[old_idx][new_idx])
                # Check for semantic domain conflict (e.g. 2.4 Disbursement vs 2.4 Organic Bonus)
                o_first = old_chunk["text"].split(":")[0].lower() if ":" in old_chunk["text"] else ""
                n_first = new_chunk["text"].split(":")[0].lower() if ":" in new_chunk["text"] else ""
                if "disbursement" in o_first and "organic" in n_first:
                    continue
                if sim < 0.25:
                    continue

                used_old_indices.add(old_idx)
                used_new_indices.add(new_idx)
                pre_type = _classify_pair_type(old_chunk["text"], new_chunk["text"], sim)
                pairs.append({
                    "old_chunk": old_chunk,
                    "new_chunk": new_chunk,
                    "similarity": round(sim, 4),
                    "change_type_pre": pre_type,
                    "matched": True,
                })
                break

    # Pass 2: High semantic similarity matching for remaining old chunks
    for old_idx, old_chunk in enumerate(old_chunks):
        if old_idx in used_old_indices:
            continue
        scores = sim_matrix[old_idx]
        best_new_idx = int(np.argmax(scores))
        best_score = float(scores[best_new_idx])

        if best_score >= MODIFIED_THRESHOLD and best_new_idx not in used_new_indices:
            used_old_indices.add(old_idx)
            used_new_indices.add(best_new_idx)
            new_chunk = new_chunks[best_new_idx]
            pre_type = _classify_pair_type(old_chunk["text"], new_chunk["text"], best_score)
            pairs.append({
                "old_chunk": old_chunk,
                "new_chunk": new_chunk,
                "similarity": round(best_score, 4),
                "change_type_pre": pre_type,
                "matched": True,
            })
        else:
            pairs.append({
                "old_chunk": old_chunk,
                "new_chunk": None,
                "similarity": round(best_score, 4) if len(scores) > 0 else 0.0,
                "change_type_pre": "REMOVED",
                "matched": False,
            })

    # Pass 3: Any new chunk not yet matched -> ADDED
    for new_idx, new_chunk in enumerate(new_chunks):
        if new_idx not in used_new_indices:
            pairs.append({
                "old_chunk": None,
                "new_chunk": new_chunk,
                "similarity": 0.0,
                "change_type_pre": "ADDED",
                "matched": False,
            })

    # Sort pairs by natural document order
    pairs.sort(key=_get_pair_sort_key)

    logger.info(
        f"Aligned {len(old_chunks)} old + {len(new_chunks)} new chunks -> {len(pairs)} pairs "
        f"({sum(1 for p in pairs if p['change_type_pre'] == 'MODIFIED')} modified, "
        f"{sum(1 for p in pairs if p['change_type_pre'] == 'ADDED')} added, "
        f"{sum(1 for p in pairs if p['change_type_pre'] == 'REMOVED')} removed, "
        f"{sum(1 for p in pairs if p['change_type_pre'] == 'SEMANTICALLY_EQUIVALENT')} semantically equivalent, "
        f"{sum(1 for p in pairs if p['change_type_pre'] == 'UNCHANGED')} unchanged)"
    )
    return pairs


def _classify_pair_type(old_text: str, new_text: str, sim: float) -> str:
    """Classifies pair into UNCHANGED, SEMANTICALLY_EQUIVALENT, or MODIFIED."""
    o_body = strip_clause_identifier(old_text)
    n_body = strip_clause_identifier(new_text)

    # 1. Exact or formatting-only difference in body
    if is_formatting_only_diff(o_body, n_body):
        return "UNCHANGED"

    # 2. Check if numeric tokens differ
    tokens_old = extract_critical_tokens(o_body)
    tokens_new = extract_critical_tokens(n_body)
    if tokens_old != tokens_new:
        return "MODIFIED"

    # 3. High cosine with identical numeric tokens
    if sim >= EQUIVALENT_THRESHOLD:
        return "SEMANTICALLY_EQUIVALENT"

    return "MODIFIED"


def _get_pair_sort_key(p: Dict) -> tuple:
    """Provides a deterministic sort key matching document flow."""
    chunk = p.get("new_chunk") or p.get("old_chunk") or {}
    sec = chunk.get("section_title", "")
    sub = chunk.get("section_number", "")

    # Common policy section ordering
    sec_order = {
        "Introduction": 0,
        "Document Content": 0,
        "ELIGIBILITY CRITERIA": 1,
        "FINANCIAL ASSISTANCE & SUBSIDY": 2,
        "APPLICATION DEADLINE & TIMELINE": 3,
        "DOCUMENTATION REQUIREMENTS": 4,
        "BENEFICIARY COVERAGE": 5,
        "ADMINISTRATIVE PROCEDURE": 6,
        "MONITORING & AUDIT": 7,
        "MONITORING & GRIEVANCE REDRESSAL": 7,
    }
    s_idx = sec_order.get(sec, 99)

    sub_str = str(sub or "")
    m = re.match(r"^(\d+)\.?(\d+)?", sub_str)
    if m:
        major = int(m.group(1))
        minor = int(m.group(2)) if m.group(2) else 0
        sub_key = (major, minor)
    elif sub_str.startswith("a)"):
        sub_key = (4, 1, 1)
    elif sub_str.startswith("b)"):
        sub_key = (4, 1, 2)
    elif sub_str.startswith("c)"):
        sub_key = (4, 1, 3)
    elif sub_str.startswith("d)"):
        sub_key = (4, 1, 4)
    elif sub_str.startswith("e)"):
        sub_key = (4, 1, 5)
    else:
        sub_key = (99, 99)

    p_num = chunk.get("page_start", 1)
    return (p_num, s_idx, sub_key)



def _all_as_added_or_removed(old_chunks: List[Dict], new_chunks: List[Dict]) -> List[Dict]:
    pairs = []
    for c in old_chunks:
        pairs.append({"old_chunk": c, "new_chunk": None, "similarity": 0.0, "change_type_pre": "REMOVED", "matched": False})
    for c in new_chunks:
        pairs.append({"old_chunk": None, "new_chunk": c, "similarity": 0.0, "change_type_pre": "ADDED", "matched": False})
    return pairs
