import json
import unittest
from unittest.mock import MagicMock, patch

from backend.agents.chunk_summary_agent import summarize_chunk
from backend.agents.analysis_agent import analyze_transcript
from backend.agents.research_agent import research_claim
from backend.agents.writer_agent import write_article
from backend.agents.guardrail_agent import check_article
from backend.agents.critic_agent import critique_article


class TestAgentsWithMockedLLM(unittest.TestCase):
    @patch("backend.agents.chunk_summary_agent.openai_client")
    def test_chunk_summary_agent(self, mock_client):
        expected_output = {
            "chunk_id": 1,
            "summary": "The speakers discussed the origins of Python.",
            "key_points": [
                {"point": "Python was created in 1991", "timestamp": "01:15"}
            ],
        }
        mock_resp = MagicMock()
        mock_resp.output_text = json.dumps(expected_output)
        mock_client.responses.create.return_value = mock_resp

        chunk = {
            "chunk_id": 1,
            "start_timestamp": "00:00",
            "end_timestamp": "05:00",
            "segments": [{"timestamp": "01:15", "text": "Python created in 1991"}],
        }

        result = summarize_chunk(chunk)
        self.assertEqual(result["chunk_id"], 1)
        self.assertEqual(len(result["key_points"]), 1)
        mock_client.responses.create.assert_called_once()

    @patch("backend.agents.analysis_agent.client")
    def test_analysis_agent(self, mock_client):
        expected_analysis = {
            "speakers": ["Host"],
            "topics": ["Programming"],
            "claims": [
                {
                    "claim": "Python was created in 1991",
                    "speaker": "Host",
                    "timestamp": "01:15",
                    "claim_type": "FACTUAL",
                    "priority": "HIGH",
                    "requires_verification": True,
                }
            ],
            "quotes": [
                {
                    "quote": "Python was created in 1991",
                    "speaker": "Host",
                    "timestamp": "01:15",
                }
            ],
            "agreements": ["Python is popular."],
            "disagreements": [],
        }
        mock_resp = MagicMock()
        mock_resp.output_text = json.dumps(expected_analysis)
        mock_client.responses.create.return_value = mock_resp

        result = analyze_transcript(
            transcript="[01:15] Python was created in 1991",
            chunk_summaries=[{"chunk_id": 1, "summary": "Discussed Python"}],
        )

        self.assertEqual(result["speakers"], ["Host"])
        self.assertEqual(len(result["claims"]), 1)
        self.assertEqual(result["claims"][0]["claim_type"], "FACTUAL")

    @patch("backend.agents.research_agent.openai_client")
    @patch("backend.agents.research_agent.tavily_client")
    def test_research_agent(self, mock_tavily, mock_openai):
        # Mock Tavily search results
        mock_tavily.search.return_value = {
            "results": [
                {
                    "title": "History of Python",
                    "url": "https://example.com/python",
                    "content": "Python 0.9.0 was released in February 1991.",
                }
            ]
        }

        # Mock OpenAI evaluation
        expected_research = {
            "claim": "Python was created in 1991",
            "status": "SUPPORTED",
            "explanation": "Verified from authoritative historical records.",
            "sources": [
                {
                    "title": "History of Python",
                    "url": "https://example.com/python",
                }
            ],
        }
        mock_resp = MagicMock()
        mock_resp.output_text = json.dumps(expected_research)
        mock_openai.responses.create.return_value = mock_resp

        claim = {
            "claim": "Python was created in 1991",
            "claim_type": "FACTUAL",
            "priority": "HIGH",
        }
        result = research_claim(claim)

        self.assertEqual(result["status"], "SUPPORTED")
        self.assertEqual(len(result["sources"]), 1)

    @patch("backend.agents.writer_agent.client")
    def test_writer_agent(self, mock_client):
        expected_article = {
            "title": "The Genesis of Python",
            "summary": "How Python began in 1991.",
            "article": "Python was released in 1991 by Guido van Rossum.",
        }
        mock_resp = MagicMock()
        mock_resp.output_text = json.dumps(expected_article)
        mock_client.responses.create.return_value = mock_resp

        result = write_article(
            transcript="Sample transcript",
            analysis={"topics": ["Python"], "claims": []},
            research=[{"claim": "Python created in 1991", "status": "SUPPORTED", "explanation": "True", "sources": []}],
        )

        self.assertEqual(result["title"], "The Genesis of Python")
        self.assertIn("Python was released", result["article"])

    @patch("backend.agents.guardrail_agent.client")
    def test_guardrail_agent(self, mock_client):
        expected_guardrail = {
            "passed": True,
            "violations": [],
            "summary": "All checks passed cleanly.",
        }
        mock_resp = MagicMock()
        mock_resp.output_text = json.dumps(expected_guardrail)
        mock_client.responses.create.return_value = mock_resp

        result = check_article(
            transcript="[01:15] Python created in 1991",
            research=[],
            article={"title": "Python", "summary": "Sum", "article": "Python created in 1991"},
        )

        self.assertTrue(result["passed"])
        self.assertEqual(result["violations"], [])

    @patch("backend.agents.critic_agent.client")
    def test_critic_agent(self, mock_client):
        expected_critique = {
            "needs_revision": True,
            "overall_feedback": "Fix attribution in paragraph 2.",
            "revision_instructions": ["Remove quote not found in transcript."],
        }
        mock_resp = MagicMock()
        mock_resp.output_text = json.dumps(expected_critique)
        mock_client.responses.create.return_value = mock_resp

        result = critique_article(
            article={"title": "Python", "summary": "Sum", "article": "Some quote"},
            guardrail_result={"passed": False, "violations": [{"type": "QUOTE_MISMATCH"}]},
        )

        self.assertTrue(result["needs_revision"])
        self.assertEqual(len(result["revision_instructions"]), 1)


if __name__ == "__main__":
    unittest.main()

