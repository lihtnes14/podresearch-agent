"""Evaluation metrics for PodResearch Agent:
1. Faithfulness (Factual Grounding)
2. Answer Relevancy (Podcast Alignment)
3. Revision Success Rate (Critic-Writer Loop)
4. Precision (Correctness of Guardrail Flags)
5. Recall (Ability to Detect Violations)
6. End-to-End Latency (Performance & SLAs)
"""
from evals.metrics.faithfulness import evaluate_faithfulness
from evals.metrics.answer_relevancy import evaluate_answer_relevancy
from evals.metrics.revision_success import evaluate_revision_cycle
from evals.metrics.precision_recall import evaluate_guardrail_precision_recall
from evals.metrics.latency import evaluate_latency_performance

__all__ = [
    "evaluate_faithfulness",
    "evaluate_answer_relevancy",
    "evaluate_revision_cycle",
    "evaluate_guardrail_precision_recall",
    "evaluate_latency_performance",
]
