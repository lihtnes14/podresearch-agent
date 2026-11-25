import unittest

from evals.datasets.golden_podcast_data import (
    CLEAN_VALID_ARTICLE,
    GOLDEN_TRANSCRIPT,
    GOLDEN_RESEARCH_RESULTS,
    GOLDEN_PODCAST_TOPICS,
    GOLDEN_PODCAST_KEY_POINTS,
    HALLUCINATED_UNGROUNDED_ARTICLE,
    GOLDEN_REVISION_PAIR,
    CORRUPTED_ARTICLE_QUOTE_MISMATCH,
    CORRUPTED_ARTICLE_UNSUPPORTED_CLAIM,
    CORRUPTED_ARTICLE_MISATTRIBUTION,
)
from evals.metrics.faithfulness import evaluate_faithfulness
from evals.metrics.answer_relevancy import evaluate_answer_relevancy
from evals.metrics.revision_success import evaluate_revision_cycle
from evals.metrics.precision_recall import evaluate_guardrail_precision_recall
from evals.metrics.latency import evaluate_latency_performance
from evals.runner import run_all_evaluations


class TestAgenticEvaluations(unittest.TestCase):
    def test_01_faithfulness_metric(self):
        # 1. Clean valid article should have high faithfulness
        result_clean = evaluate_faithfulness(
            article=CLEAN_VALID_ARTICLE,
            raw_transcript=GOLDEN_TRANSCRIPT,
            verified_research=GOLDEN_RESEARCH_RESULTS,
        )
        self.assertTrue(result_clean["passed"])
        self.assertGreaterEqual(result_clean["faithfulness_score"], 0.85)
        self.assertEqual(result_clean["ungrounded_statements"], 0)

        # 2. Hallucinated article should fail faithfulness
        result_hallucinated = evaluate_faithfulness(
            article=HALLUCINATED_UNGROUNDED_ARTICLE,
            raw_transcript=GOLDEN_TRANSCRIPT,
            verified_research=GOLDEN_RESEARCH_RESULTS,
        )
        self.assertFalse(result_hallucinated["passed"])
        self.assertLess(result_hallucinated["faithfulness_score"], 0.50)
        self.assertGreater(result_hallucinated["ungrounded_statements"], 0)

    def test_02_answer_relevancy_metric(self):
        # 1. Clean article focused on podcast topics should pass
        result_relevant = evaluate_answer_relevancy(
            article=CLEAN_VALID_ARTICLE,
            podcast_topics=GOLDEN_PODCAST_TOPICS,
            podcast_key_points=GOLDEN_PODCAST_KEY_POINTS,
        )
        self.assertTrue(result_relevant["passed"])
        self.assertGreaterEqual(result_relevant["relevancy_score"], 0.80)
        self.assertGreaterEqual(result_relevant["topic_coverage_rate"], 0.75)

        # 2. Off-topic article should fail relevancy
        off_topic_article = {
            "title": "Cooking Recipes for Italian Pasta",
            "summary": "How to make authentic carbonara and marinara sauce.",
            "article": "Boil salted water and add spaghetti. Sauté pancetta with black pepper.",
        }
        result_off_topic = evaluate_answer_relevancy(
            article=off_topic_article,
            podcast_topics=GOLDEN_PODCAST_TOPICS,
            podcast_key_points=GOLDEN_PODCAST_KEY_POINTS,
        )
        self.assertFalse(result_off_topic["passed"])
        self.assertEqual(result_off_topic["topic_coverage_rate"], 0.0)

    def test_03_revision_success_rate_metric(self):
        result = evaluate_revision_cycle(revision_cases=[GOLDEN_REVISION_PAIR])
        self.assertTrue(result["passed"])
        self.assertEqual(result["revision_success_rate"], 1.0)
        self.assertEqual(result["violation_reduction_rate"], 1.0)
        self.assertEqual(result["total_remaining_violations"], 0)

    def test_04_precision_and_recall_metrics(self):
        clean_evals = [
            {"passed": True, "violations": []},
            {"passed": True, "violations": []},
        ]
        corrupted_evals = [
            {
                "guardrail_result": {
                    "passed": False,
                    "violations": [{"type": "QUOTE_MISMATCH"}],
                },
                "actual_violations_count": 1,
                "expected_violation_types": ["QUOTE_MISMATCH"],
            },
            {
                "guardrail_result": {
                    "passed": False,
                    "violations": [{"type": "UNSUPPORTED_CLAIM"}],
                },
                "actual_violations_count": 1,
                "expected_violation_types": ["UNSUPPORTED_CLAIM"],
            },
            {
                "guardrail_result": {
                    "passed": False,
                    "violations": [{"type": "MISATTRIBUTION"}],
                },
                "actual_violations_count": 1,
                "expected_violation_types": ["MISATTRIBUTION"],
            },
        ]

        result = evaluate_guardrail_precision_recall(
            clean_article_evaluations=clean_evals,
            corrupted_article_evaluations=corrupted_evals,
        )

        self.assertTrue(result["passed"])
        self.assertEqual(result["precision"], 1.0)  # Zero false positives on clean articles
        self.assertEqual(result["recall"], 1.0)     # All 3 injected defects detected
        self.assertEqual(result["f1_score"], 1.0)
        self.assertEqual(result["false_positives"], 0)
        self.assertEqual(result["false_negatives"], 0)

    def test_05_latency_performance_metric(self):
        # 1. Within SLA thresholds
        normal_latencies = {
            "transcript": 1.2,
            "chunking": 0.1,
            "analysis": 3.5,
            "research": 5.0,
            "writer": 3.0,
            "guardrail": 2.0,
            "total_pipeline": 14.8,
        }
        res_normal = evaluate_latency_performance(normal_latencies)
        self.assertTrue(res_normal["passed"])
        self.assertEqual(res_normal["sla_compliance_rate"], 1.0)

        # 2. Exceeding SLA threshold
        slow_latencies = {
            "transcript": 12.0,
            "total_pipeline": 120.0,
        }
        res_slow = evaluate_latency_performance(slow_latencies)
        self.assertFalse(res_slow["passed"])
        self.assertLess(res_slow["sla_compliance_rate"], 0.85)

    def test_06_full_evaluation_runner_composite(self):
        report = run_all_evaluations()

        # Composite score must be >= 90%
        self.assertGreaterEqual(
            report["composite_score"],
            90.0,
            f"Composite eval score was {report['composite_score']}%",
        )

        # Core 6 metrics must all pass
        metrics = report["metrics"]
        self.assertTrue(metrics["faithfulness"]["passed"])
        self.assertTrue(metrics["answer_relevancy"]["passed"])
        self.assertTrue(metrics["revision_success_rate"]["passed"])
        self.assertTrue(metrics["precision"]["passed"])
        self.assertTrue(metrics["recall"]["passed"])
        self.assertTrue(metrics["end_to_end_latency"]["passed"])


if __name__ == "__main__":
    unittest.main()
