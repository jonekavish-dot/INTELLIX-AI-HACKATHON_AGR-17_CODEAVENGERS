"""
AgriDiff AI — Textual Differ
Computes character/word-level textual differences using Python's difflib.
This is Level 1 of the three-level intelligence model.
"""

import difflib
import logging
from typing import List, Dict

logger = logging.getLogger("agridiff.differ")


def compute_textual_diff(pairs: List[Dict]) -> List[Dict]:
    """
    For each aligned pair, compute textual diff ratio and inline diff.
    Adds: textual_diff_ratio, diff_ops, has_textual_change
    """
    result = []
    for pair in pairs:
        old_text = pair["old_chunk"]["text"] if pair["old_chunk"] else ""
        new_text = pair["new_chunk"]["text"] if pair["new_chunk"] else ""

        ratio, diff_ops = _compute_diff(old_text, new_text)

        pair["textual_diff_ratio"] = round(1.0 - ratio, 4)  # ratio of CHANGED content
        pair["diff_ops"] = diff_ops
        pair["has_textual_change"] = ratio < 0.999
        result.append(pair)

    return result


def _compute_diff(old: str, new: str) -> tuple[float, List[Dict]]:
    """
    Returns (similarity_ratio, list_of_diff_ops).
    similarity_ratio: 0.0 = completely different, 1.0 = identical.
    """
    if not old and not new:
        return 1.0, []
    if not old:
        return 0.0, [{"op": "insert", "text": new}]
    if not new:
        return 0.0, [{"op": "delete", "text": old}]

    # Word-level diff for better readability
    old_words = old.split()
    new_words = new.split()

    matcher = difflib.SequenceMatcher(None, old_words, new_words, autojunk=False)
    ratio = matcher.ratio()

    ops = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            ops.append({"op": "equal", "text": " ".join(old_words[i1:i2])})
        elif tag == "replace":
            ops.append({"op": "delete", "text": " ".join(old_words[i1:i2])})
            ops.append({"op": "insert", "text": " ".join(new_words[j1:j2])})
        elif tag == "delete":
            ops.append({"op": "delete", "text": " ".join(old_words[i1:i2])})
        elif tag == "insert":
            ops.append({"op": "insert", "text": " ".join(new_words[j1:j2])})

    return ratio, ops


def get_inline_diff_html(old: str, new: str) -> str:
    """Generate simple inline diff HTML for frontend display."""
    old_words = old.split()
    new_words = new.split()
    matcher = difflib.SequenceMatcher(None, old_words, new_words, autojunk=False)

    old_html, new_html = [], []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            txt = " ".join(old_words[i1:i2])
            old_html.append(txt)
            new_html.append(txt)
        elif tag == "replace":
            old_html.append(f'<del>{" ".join(old_words[i1:i2])}</del>')
            new_html.append(f'<ins>{" ".join(new_words[j1:j2])}</ins>')
        elif tag == "delete":
            old_html.append(f'<del>{" ".join(old_words[i1:i2])}</del>')
        elif tag == "insert":
            new_html.append(f'<ins>{" ".join(new_words[j1:j2])}</ins>')

    return {
        "old_html": " ".join(old_html),
        "new_html": " ".join(new_html),
    }
