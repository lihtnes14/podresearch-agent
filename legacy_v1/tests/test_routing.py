import unittest
from backend.graph.workflow import route_after_memory, route_after_guardrail


class TestWorkflowRouting(unittest.TestCase):
    def test_route_after_memory_missing_transcript(self):
        state = {"loaded_artifacts": []}
        self.assertEqual(route_after_memory(state), "transcript")

    def test_route_after_memory_missing_analysis(self):
        state = {"loaded_artifacts": ["transcript"]}
        self.assertEqual(route_after_memory(state), "analysis")

    def test_route_after_memory_missing_research(self):
        state = {"loaded_artifacts": ["transcript", "analysis"]}
        self.assertEqual(route_after_memory(state), "memory_retrieval")

    def test_route_after_memory_missing_article(self):
        state = {"loaded_artifacts": ["transcript", "analysis", "research"]}
        self.assertEqual(route_after_memory(state), "writer")

    def test_route_after_memory_missing_guardrail(self):
        state = {"loaded_artifacts": ["transcript", "analysis", "research", "article"]}
        self.assertEqual(route_after_memory(state), "guardrail")

    def test_route_after_memory_all_loaded(self):
        state = {
            "loaded_artifacts": [
                "transcript",
                "analysis",
                "research",
                "article",
                "guardrail",
            ]
        }
        self.assertEqual(route_after_memory(state), "end")

    def test_route_after_guardrail_passed(self):
        state = {
            "session_id": "test_session_id",
            "revision_count": 0,
            "guardrail_result": {
                "passed": True,
                "violations": [],
                "summary": "Passed cleanly.",
            },
        }
        self.assertEqual(route_after_guardrail(state), "end")

    def test_route_after_guardrail_max_revisions_reached(self):
        state = {
            "session_id": "test_session_id",
            "revision_count": 2,
            "guardrail_result": {
                "passed": False,
                "violations": [{"type": "QUOTE_MISMATCH", "severity": "HIGH"}],
                "summary": "Failed.",
            },
        }
        self.assertEqual(route_after_guardrail(state), "end")

    def test_route_after_guardrail_evidence_issue_routes_to_research(self):
        # UNSUPPORTED_CLAIM or HALLUCINATION routes to research node
        for issue_type in ["UNSUPPORTED_CLAIM", "HALLUCINATION"]:
            state = {
                "session_id": "test_session_id",
                "revision_count": 0,
                "guardrail_result": {
                    "passed": False,
                    "violations": [
                        {
                            "type": issue_type,
                            "severity": "HIGH",
                            "article_text": "sample text",
                            "explanation": "sample explanation",
                        }
                    ],
                    "summary": f"Failed with {issue_type}.",
                },
            }
            self.assertEqual(
                route_after_guardrail(state),
                "research",
                f"Failed to route {issue_type} to research",
            )

    def test_route_after_guardrail_other_violations_route_to_critic(self):
        # Formatting, misattribution, or quote mismatch routes to critic
        for issue_type in ["QUOTE_MISMATCH", "MISATTRIBUTION", "OPINION_AS_FACT"]:
            state = {
                "session_id": "test_session_id",
                "revision_count": 0,
                "guardrail_result": {
                    "passed": False,
                    "violations": [
                        {
                            "type": issue_type,
                            "severity": "MEDIUM",
                            "article_text": "sample text",
                            "explanation": "sample explanation",
                        }
                    ],
                    "summary": f"Failed with {issue_type}.",
                },
            }
            self.assertEqual(
                route_after_guardrail(state),
                "critic",
                f"Failed to route {issue_type} to critic",
            )


if __name__ == "__main__":
    unittest.main()

