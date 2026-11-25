"""Metrics: Guardrail Precision & Recall.
- Precision: Correctness of guardrail flags (True Positives / (True Positives + False Positives)).
  Evaluates whether the Guardrail avoids raising false alarms on clean, factual text.
- Recall: Ability to detect actual violations (True Positives / (True Positives + False Negatives)).
  Evaluates whether the Guardrail catches all ground-truth defects injected into drafts.

Target: Precision >= 0.85, Recall >= 0.85
"""
from __future__ import annotations



def evaluate_guardrail_precision_recall(
    clean_article_evaluations: list[dict],
    corrupted_article_evaluations: list[dict],
) -> dict:
    """Computes Precision, Recall, and F1 for the Guardrail Agent.

    clean_article_evaluations: List of guardrail results for articles known to be clean (should have 0 violations).
    corrupted_article_evaluations: List of dicts with:
      - 'guardrail_result': The agent's output
      - 'actual_violations_count': Number of injected ground-truth defects
      - 'expected_violation_types': List of expected violation types
    """
    # 1. False Positives from clean articles: Any violation flagged on a clean article is a False Positive (FP)
    false_positives = 0
    clean_passed_count = 0
    for res in clean_article_evaluations:
        flagged_violations = len(res.get("violations", []))
        if flagged_violations > 0:
            false_positives += flagged_violations
        else:
            clean_passed_count += 1

    # 2. Evaluate corrupted articles for True Positives (TP) and False Negatives (FN)
    true_positives = 0
    false_negatives = 0
    total_injected_defects = 0

    for case in corrupted_article_evaluations:
        result = case.get("guardrail_result", {})
        actual_count = case.get("actual_violations_count", 1)
        expected_types = [t.upper() for t in case.get("expected_violation_types", [])]

        total_injected_defects += actual_count
        detected_violations = result.get("violations", [])

        # Match detected violations to expected types
        matched_in_case = 0
        for v in detected_violations:
            v_type = v.get("type", "").upper()
            if not expected_types or v_type in expected_types:
                matched_in_case += 1

        # Cap matched to actual_count
        tp_for_case = min(matched_in_case, actual_count)
        fn_for_case = max(0, actual_count - tp_for_case)
        # Any extra unmatched violations in a corrupted case are either extra detections or FP
        fp_for_case = max(0, len(detected_violations) - tp_for_case)

        true_positives += tp_for_case
        false_negatives += fn_for_case
        false_positives += fp_for_case

    # Precision: TP / (TP + FP)
    denom_precision = true_positives + false_positives
    precision = (
        round(true_positives / denom_precision, 4) if denom_precision > 0 else 1.0
    )

    # Recall: TP / (TP + FN)
    denom_recall = true_positives + false_negatives
    recall = round(true_positives / denom_recall, 4) if denom_recall > 0 else 1.0

    # F1 Score
    if precision + recall > 0:
        f1_score = round(2 * (precision * recall) / (precision + recall), 4)
    else:
        f1_score = 0.0

    overall_score = round((0.5 * precision) + (0.5 * recall), 4)

    return {
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "total_injected_defects": total_injected_defects,
        "clean_articles_tested": len(clean_article_evaluations),
        "clean_articles_passed": clean_passed_count,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "overall_score": overall_score,
        "passed": (precision >= 0.85) and (recall >= 0.85),
    }
