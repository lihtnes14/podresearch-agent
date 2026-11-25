import json
from unittest.mock import MagicMock
import pytest


@pytest.fixture
def sample_transcript():
    return """[00:05] Welcome to today's episode on modern software engineering.
[01:15] Python was created by Guido van Rossum and released in 1991.
[05:20] Many distributed systems rely on the Raft consensus algorithm.
[10:45] Java was designed by James Gosling at Sun Microsystems.
[15:10] I think functional programming is strictly superior to object-oriented programming.
[20:30] Check out our sponsor at example.com/podcast for a discount.
[105:00] In conclusion, choosing the right tool for the job is what matters most.
"""


@pytest.fixture
def sample_chunk():
    return {
        "chunk_id": 1,
        "start_timestamp": "00:00",
        "end_timestamp": "05:00",
        "segments": [
            {"timestamp": "00:05", "text": "Welcome to today's episode on modern software engineering."},
            {"timestamp": "01:15", "text": "Python was created by Guido van Rossum and released in 1991."},
        ],
    }


@pytest.fixture
def sample_analysis():
    return {
        "speakers": ["Host", "Guest"],
        "topics": ["Programming Languages", "Distributed Systems"],
        "claims": [
            {
                "claim": "Python was created by Guido van Rossum and released in 1991.",
                "speaker": "Host",
                "timestamp": "01:15",
                "claim_type": "FACTUAL",
                "priority": "HIGH",
                "requires_verification": True,
            },
            {
                "claim": "Java was designed by James Gosling at Sun Microsystems.",
                "speaker": "Guest",
                "timestamp": "10:45",
                "claim_type": "FACTUAL",
                "priority": "HIGH",
                "requires_verification": True,
            },
            {
                "claim": "Functional programming is strictly superior to OOP.",
                "speaker": "Host",
                "timestamp": "15:10",
                "claim_type": "OPINION",
                "priority": "LOW",
                "requires_verification": False,
            },
        ],
        "quotes": [
            {
                "quote": "Python was created by Guido van Rossum and released in 1991.",
                "speaker": "Host",
                "timestamp": "01:15",
            }
        ],
        "agreements": ["Tool selection depends on context."],
        "disagreements": ["OOP vs Functional paradigms."],
    }


@pytest.fixture
def sample_research():
    return [
        {
            "claim": "Python was created by Guido van Rossum and released in 1991.",
            "status": "SUPPORTED",
            "explanation": "Guido van Rossum began developing Python in December 1989 and released version 0.9.0 in February 1991.",
            "sources": [
                {
                    "title": "History of Python",
                    "url": "https://en.wikipedia.org/wiki/History_of_Python",
                }
            ],
        }
    ]


@pytest.fixture
def sample_article():
    return {
        "title": "The Evolution of Modern Programming Languages",
        "summary": "An exploration of Python and Java origins discussed during the podcast.",
        "article": "Python was developed by Guido van Rossum in 1991. The language was conceived as a successor to ABC.",
    }


@pytest.fixture
def sample_guardrail_pass():
    return {
        "passed": True,
        "violations": [],
        "summary": "All factual claims and quotes are fully verified.",
    }


@pytest.fixture
def sample_guardrail_fail_unsupported():
    return {
        "passed": False,
        "violations": [
            {
                "type": "UNSUPPORTED_CLAIM",
                "severity": "HIGH",
                "article_text": "Python was originally written entirely in Assembly.",
                "explanation": "Evidence shows Python was written in C, not Assembly.",
            }
        ],
        "summary": "Article contains an unsupported claim regarding implementation language.",
    }


@pytest.fixture
def sample_guardrail_fail_quote():
    return {
        "passed": False,
        "violations": [
            {
                "type": "QUOTE_MISMATCH",
                "severity": "MEDIUM",
                "article_text": "I despise all imperative code.",
                "explanation": "This quote does not appear anywhere in the transcript.",
            }
        ],
        "summary": "Article attributes a quote that does not exist in the source transcript.",
    }


def make_mock_openai_response(data: dict):
    """Helper to mock openai_client.responses.create response."""
    mock_resp = MagicMock()
    mock_resp.output_text = json.dumps(data)
    return mock_resp

