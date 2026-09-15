"""
AgriDiff AI — Benchmark Evaluation Script
Measures change detection precision, recall, F1, and evidence grounding against canonical ground truth.
BIT-AI-001 | AGR-17 | Team CODEAVENGERS

Usage:
    python evaluation/eval.py --results results.json --ground_truth data/ground_truth.json
"""

import json
import argparse
import sys
from typing import List, Dict


def load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fuzzy_match(detected: Dict, truth: Dict) -> bool:
    """
    Match a detected change to a ground truth change.
    Match criteria: matching section or field, and consistent category.
    """
    det_sec = (detected.get("section") or detected.get("section_title") or "").lower()
    truth_sec = (truth.get("section") or "").lower()
    
    det_field = (detected.get("field") or "").lower()
    truth_field = (truth.get("field") or "").lower()

    # Section match
    sec_match = (truth_sec in det_sec) or (det_sec in truth_sec)
    
    # Field match if both defined
    field_match = bool(det_field and truth_field and (det_field == truth_field))

    # Category match
    cat_match = detected.get("category", "").lower() == truth.get("category", "").lower()

    return (sec_match and cat_match) or field_match


def evaluate(results: Dict, ground_truth: Dict) -> Dict:
    # Support both canonical all_changes and legacy changes
    detected_changes = results.get("all_changes") or results.get("changes") or []
    truth_changes = ground_truth.get("changes", [])

    if not detected_changes:
        print("[WARNING] No changes detected in results payload.")
        return {}

    if not truth_changes:
        print("[WARNING] Ground truth is empty.")
        return {}

    # ── Change Detection Precision & Recall ────────────────────────────────────
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
        if (d.get("impact") or d.get("severity", "")).upper() == (t.get("impact") or t.get("severity", "")).upper()
    )
    type_correct = sum(
        1 for d, t in true_positives
        if d.get("change_type", "").upper() == t.get("change_type", "").upper()
    )

    cat_acc = cat_correct / tp if tp > 0 else 0.0
    sev_acc = sev_correct / tp if tp > 0 else 0.0
    type_acc = type_correct / tp if tp > 0 else 0.0

    # ── Evidence Grounding Rate ────────────────────────────────────────────────
    grounded = sum(
        1 for c in detected_changes
        if c.get("evidence_status") == "SUPPORTED"
    )
    grounding_rate = grounded / len(detected_changes) if detected_changes else 1.0

    return {
        "dataset": {
            "name": ground_truth.get("dataset", "AgriDiff Benchmark"),
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
            "impact_accuracy": round(sev_acc, 3),
            "change_type_accuracy": round(type_acc, 3),
        },
        "grounding": {
            "evidence_grounding_rate": round(grounding_rate, 3),
            "grounded_changes": grounded,
            "total_evaluated": len(detected_changes),
        },
        "avg_confidence": round(
            sum(c.get("confidence", 0.8) for c in detected_changes) / len(detected_changes), 3
        ) if detected_changes else 0.85,
    }


def print_report(metrics: Dict):
    if not metrics:
        return
    print("\n" + "=" * 55)
    print("  AgriDiff AI — Benchmark Evaluation Report")
    print("  Team: CODEAVENGERS | BIT-AI-001 | AGR-17")
    print("=" * 55)
    ds = metrics["dataset"]
    print(f"\n  Dataset: {ds['name']}")
    print(f"  Ground Truth Benchmark: {ds['ground_truth_changes']} known changes")
    print(f"  Detected Changes:       {ds['detected_changes']}")

    cd = metrics["change_detection"]
    print(f"\n  [EXHAUSTIVENESS & ACCURACY]")
    print(f"    True Positives:       {cd['true_positives']}")
    print(f"    False Positives:      {cd['false_positives']}")
    print(f"    False Negatives:      {cd['false_negatives']}")
    print(f"    Precision:            {cd['precision'] * 100:.1f}%")
    print(f"    Recall:               {cd['recall'] * 100:.1f}%")
    print(f"    F1 Score:             {cd['f1_score'] * 100:.1f}%")

    ca = metrics["classification_accuracy"]
    print(f"\n  [CLASSIFICATION QUALITY]")
    print(f"    Category Accuracy:    {ca['category_accuracy'] * 100:.1f}%")
    print(f"    Impact Accuracy:      {ca['impact_accuracy'] * 100:.1f}%")
    print(f"    Change Type Accuracy: {ca['change_type_accuracy'] * 100:.1f}%")

    gr = metrics["grounding"]
    print(f"\n  [EVIDENCE GROUNDING]")
    print(f"    Verified Grounded:    {gr['grounded_changes']} / {gr['total_evaluated']}")
    print(f"    Grounding Rate:       {gr['evidence_grounding_rate'] * 100:.1f}%")
    print(f"    Avg Confidence:       {metrics['avg_confidence'] * 100:.1f}%")
    print("\n" + "=" * 55 + "\n")


def main():
    parser = argparse.ArgumentParser(description="AgriDiff AI Evaluation")
    parser.add_argument("--results", required=True, help="Path to comparison results JSON")
    parser.add_argument("--ground_truth", required=True, help="Path to benchmark ground truth JSON")
    parser.add_argument("--output", help="Optional output JSON path for metrics")
    args = parser.parse_args()

    try:
        res = load_json(args.results)
        gt = load_json(args.ground_truth)
    except Exception as e:
        print(f"[ERROR] Failed to load JSON files: {e}")
        sys.exit(1)

    m = evaluate(res, gt)
    print_report(m)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(m, f, indent=2)
        print(f"Report exported to: {args.output}")


if __name__ == "__main__":
    main()
