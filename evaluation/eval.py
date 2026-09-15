"""
AgriDiff AI — Evaluation Script
Measures change detection precision, recall, and classification accuracy.
Team: CODEAVENGERS | BIT-AI-001 | AGR-17

Usage:
    python eval.py --results results.json --ground_truth ground_truth.json
"""

import json
import argparse
import sys
from typing import List, Dict


def load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fuzzy_match(detected: Dict, truth: Dict, threshold: float = 0.6) -> bool:
    """
    Match a detected change to a ground truth change.
    Match criteria: same section (partial string match) AND same category.
    """
    section_match = (
        truth["section"].lower() in detected.get("section_title", "").lower()
        or detected.get("section_title", "").lower() in truth["section"].lower()
    )
    category_match = detected.get("category", "").lower() == truth.get("category", "").lower()
    return section_match and category_match


def evaluate(results: Dict, ground_truth: Dict) -> Dict:
    detected_changes = results.get("changes", [])
    truth_changes = ground_truth.get("changes", [])

    if not detected_changes:
        print("⚠️  No changes detected in results file.")
        return {}

    if not truth_changes:
        print("⚠️  Ground truth is empty.")
        return {}

    # ── Change Detection ───────────────────────────────────────────────────────
    matched_truth = set()
    true_positives = []

    for detected in detected_changes:
        for i, truth in enumerate(truth_changes):
            if i not in matched_truth and fuzzy_match(detected, truth):
                matched_truth.add(i)
                true_positives.append((detected, truth))
                break

    tp = len(true_positives)
    fp = len(detected_changes) - tp
    fn = len(truth_changes) - tp

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    # ── Classification Accuracy ────────────────────────────────────────────────
    cat_correct = sum(
        1 for d, t in true_positives
        if d.get("category", "").lower() == t.get("category", "").lower()
    )
    sev_correct = sum(
        1 for d, t in true_positives
        if d.get("severity", "").upper() == t.get("severity", "").upper()
    )
    type_correct = sum(
        1 for d, t in true_positives
        if d.get("change_type", "").upper() == t.get("change_type", "").upper()
    )

    cat_acc = cat_correct / tp if tp > 0 else 0.0
    sev_acc = sev_correct / tp if tp > 0 else 0.0
    type_acc = type_correct / tp if tp > 0 else 0.0

    # ── Evidence Grounding ─────────────────────────────────────────────────────
    grounded = sum(
        1 for c in detected_changes
        if c.get("evidence_status") == "SUPPORTED"
        or c.get("old_evidence") not in (None, "INSUFFICIENT_EVIDENCE")
        or c.get("new_evidence") not in (None, "INSUFFICIENT_EVIDENCE")
    )
    grounding_rate = grounded / len(detected_changes) if detected_changes else 0.0

    # ── False Positive Rate ────────────────────────────────────────────────────
    fp_rate = fp / len(detected_changes) if detected_changes else 0.0

    return {
        "dataset": {
            "document_pair": ground_truth.get("document_pair", "Unknown"),
            "ground_truth_changes": len(truth_changes),
            "detected_changes": len(detected_changes),
        },
        "change_detection": {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1, 3),
        },
        "classification_accuracy": {
            "category_accuracy": round(cat_acc, 3),
            "severity_accuracy": round(sev_acc, 3),
            "change_type_accuracy": round(type_acc, 3),
        },
        "grounding": {
            "evidence_grounding_rate": round(grounding_rate, 3),
            "grounded_changes": grounded,
        },
        "false_positive_rate": round(fp_rate, 3),
        "avg_confidence": round(
            sum(c.get("confidence", 0) for c in detected_changes) / len(detected_changes), 3
        ) if detected_changes else 0.0,
    }


def print_report(metrics: Dict):
    print("\n" + "═" * 50)
    print("  📊 AgriDiff AI — Evaluation Results")
    print("═" * 50)
    ds = metrics["dataset"]
    print(f"\n  Dataset: {ds['document_pair']}")
    print(f"  Ground truth changes: {ds['ground_truth_changes']}")
    print(f"  Detected changes:     {ds['detected_changes']}")

    cd = metrics["change_detection"]
    print(f"\n  Change Detection")
    print(f"    True Positives:  {cd['true_positives']}")
    print(f"    False Positives: {cd['false_positives']}")
    print(f"    False Negatives: {cd['false_negatives']}")
    print(f"    Precision:       {cd['precision'] * 100:.1f}%")
    print(f"    Recall:          {cd['recall'] * 100:.1f}%")
    print(f"    F1 Score:        {cd['f1_score'] * 100:.1f}%")

    ca = metrics["classification_accuracy"]
    print(f"\n  Classification Accuracy")
    print(f"    Category:        {ca['category_accuracy'] * 100:.1f}%")
    print(f"    Severity:        {ca['severity_accuracy'] * 100:.1f}%")
    print(f"    Change Type:     {ca['change_type_accuracy'] * 100:.1f}%")

    gr = metrics["grounding"]
    print(f"\n  Evidence Grounding")
    print(f"    Rate:            {gr['evidence_grounding_rate'] * 100:.1f}%")
    print(f"    Grounded:        {gr['grounded_changes']} / {metrics['dataset']['detected_changes']}")

    print(f"\n  False Positive Rate: {metrics['false_positive_rate'] * 100:.1f}%")
    print(f"  Avg Confidence:      {metrics['avg_confidence'] * 100:.1f}%")
    print("\n" + "═" * 50 + "\n")


def main():
    parser = argparse.ArgumentParser(description="AgriDiff AI Evaluation")
    parser.add_argument("--results", required=True, help="Path to results JSON file")
    parser.add_argument("--ground_truth", required=True, help="Path to ground truth JSON file")
    parser.add_argument("--output", help="Save metrics to this JSON file (optional)")
    args = parser.parse_args()

    try:
        results = load_json(args.results)
        gt = load_json(args.ground_truth)
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        sys.exit(1)

    metrics = evaluate(results, gt)
    print_report(metrics)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        print(f"  Metrics saved to: {args.output}")


if __name__ == "__main__":
    main()
