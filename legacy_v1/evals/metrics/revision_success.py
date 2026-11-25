"""Metric: Revision Success Rate (Effectiveness of Critic–Writer Feedback).
Evaluates the multi-agent self-correction cycle:
Initial draft (failed guardrail) -> Critic feedback instructions -> Revised draft -> Guardrail re-check.

Revision Success Rate = (Repaired Drafts that now Pass) / (Total Corrupted Drafts Sent to Revision)
Violation Reduction Rate = (Initial Violations - Revised Violations) / (Initial Violations)
Target: >= 0.80
"""
from __future__ import annotations



def evaluate_revision_cycle(
    revision_cases: list[dict],
) -> dict:
    if not revision_cases:
        return {
            "total_revisions": 0,
            "successful_revisions": 0,
            "revision_success_rate": 1.0,
            "violation_reduction_rate": 1.0,
            "overall_score": 1.0,
            "passed": True,
            "details": [],
        }

    total_cases = len(revision_cases)
    repaired_count = 0
    total_initial_violations = 0
    total_remaining_violations = 0
    details = []

    for case in revision_cases:
        initial_guardrail = case.get("initial_guardrail", {})
        revised_guardrail = case.get("revised_guardrail", {})

        init_violations = len(initial_guardrail.get("violations", []))
        revised_violations = len(revised_guardrail.get("violations", []))
        revised_passed = revised_guardrail.get("passed", False)

        total_initial_violations += init_violations
        total_remaining_violations += revised_violations

        # Success requires either passing status or zero remaining violations
        is_repaired = revised_passed or (revised_violations == 0)
        if is_repaired:
            repaired_count += 1

        details.append({
            "case_id": case.get("id", "unknown"),
            "initial_violations": init_violations,
            "revised_violations": revised_violations,
            "is_repaired": is_repaired,
        })

    success_rate = repaired_count / total_cases if total_cases > 0 else 1.0

    if total_initial_violations > 0:
        reduction_rate = max(
            0.0,
            (total_initial_violations - total_remaining_violations)
            / total_initial_violations,
        )
    else:
        reduction_rate = 1.0

    overall_score = round((0.6 * success_rate) + (0.4 * reduction_rate), 4)
    passed = overall_score >= 0.80

    return {
        "total_cases": total_cases,
        "successful_revisions": repaired_count,
        "revision_success_rate": round(success_rate, 4),
        "total_initial_violations": total_initial_violations,
        "total_remaining_violations": total_remaining_violations,
        "violation_reduction_rate": round(reduction_rate, 4),
        "overall_score": overall_score,
        "passed": passed,
        "details": details,
    }
