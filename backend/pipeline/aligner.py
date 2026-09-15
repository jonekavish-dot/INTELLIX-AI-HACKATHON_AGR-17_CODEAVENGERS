"""
AgriDiff AI — Semantic Aligner
Maps old document chunks to new document chunks using cosine similarity.
Strategy: greedy best-match (fast, good enough for policy docs).
"""

import logging
import numpy as np
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("agridiff.aligner")

EQUIVALENT_THRESHOLD = 0.95   # >= this → EQUIVALENT (no meaningful change)
REWORD_THRESHOLD = 0.85       # >= this → REWORDED (structural change, not meaningful)
MODIFIED_THRESHOLD = 0.40     # >= this → MODIFIED (possible meaningful change)
# < MODIFIED_THRESHOLD with no match → ADDED or REMOVED


def align_chunks(
    old_chunks: List[Dict],
    new_chunks: List[Dict],
    old_embeddings: np.ndarray,
    new_embeddings: np.ndarray,
) -> List[Dict]:
    """
    Align old chunks to new chunks using cosine similarity.
    Returns list of aligned pair dicts with similarity scores.
    """
    if len(old_chunks) == 0 or len(new_chunks) == 0:
        logger.warning("Empty chunk list received — cannot align")
        return _all_as_added_or_removed(old_chunks, new_chunks)

    # Cosine similarity matrix: shape (M, N)
    sim_matrix = cosine_similarity(old_embeddings, new_embeddings)

    pairs = []
    used_new_indices = set()

    # For each old chunk, find its best matching new chunk
    for old_idx, old_chunk in enumerate(old_chunks):
        scores = sim_matrix[old_idx]
        best_new_idx = int(np.argmax(scores))
        best_score = float(scores[best_new_idx])

        if best_score >= MODIFIED_THRESHOLD and best_new_idx not in used_new_indices:
            used_new_indices.add(best_new_idx)
            change_type = _classify_by_similarity(best_score)
            pairs.append({
                "old_chunk": old_chunk,
                "new_chunk": new_chunks[best_new_idx],
                "similarity": round(best_score, 4),
                "change_type_pre": change_type,
                "matched": True,
            })
        else:
            # Old chunk has no good match → REMOVED
            pairs.append({
                "old_chunk": old_chunk,
                "new_chunk": None,
                "similarity": round(best_score, 4),
                "change_type_pre": "REMOVED",
                "matched": False,
            })

    # New chunks with no match → ADDED
    for new_idx, new_chunk in enumerate(new_chunks):
        if new_idx not in used_new_indices:
            pairs.append({
                "old_chunk": None,
                "new_chunk": new_chunk,
                "similarity": 0.0,
                "change_type_pre": "ADDED",
                "matched": False,
            })

    logger.info(
        f"Aligned {len(old_chunks)} old + {len(new_chunks)} new chunks → "
        f"{len(pairs)} pairs "
        f"({sum(1 for p in pairs if p['change_type_pre'] == 'MODIFIED')} modified, "
        f"{sum(1 for p in pairs if p['change_type_pre'] == 'ADDED')} added, "
        f"{sum(1 for p in pairs if p['change_type_pre'] == 'REMOVED')} removed)"
    )
    return pairs


def _classify_by_similarity(score: float) -> str:
    if score >= EQUIVALENT_THRESHOLD:
        return "EQUIVALENT"
    elif score >= REWORD_THRESHOLD:
        return "REWORDED"
    else:
        return "MODIFIED"


def _all_as_added_or_removed(old_chunks: List[Dict], new_chunks: List[Dict]) -> List[Dict]:
    pairs = []
    for c in old_chunks:
        pairs.append({"old_chunk": c, "new_chunk": None, "similarity": 0.0, "change_type_pre": "REMOVED", "matched": False})
    for c in new_chunks:
        pairs.append({"old_chunk": None, "new_chunk": c, "similarity": 0.0, "change_type_pre": "ADDED", "matched": False})
    return pairs
