"""Golden dataset for PodResearch Agent evaluation.
Curated test cases for:
1. Faithfulness (Grounded article vs Hallucinated article against transcript & research)
2. Answer Relevancy (Podcast topics and key points)
3. Revision Success Rate (Corrupted draft -> Critic instructions -> Repaired draft)
4. Precision & Recall (Clean articles vs Corrupted drafts with specific defect types)
"""

GOLDEN_TRANSCRIPT = """[00:05] Host: Welcome everyone to Tech Horizons podcast episode 42.
[00:20] Host: Today we are joined by Dr. Elena Vance to discuss software history and reliability.
[01:10] Guest: Thank you for having me. It is great to be here.
[01:45] Guest: One of the foundational moments in programming was when Python was created by Guido van Rossum and first released in 1991.
[03:20] Guest: Around four years later, Java was released by Sun Microsystems in 1995, spearheaded by James Gosling.
[05:40] Host: Personally, I believe Python is vastly more enjoyable to write than Java, though that is obviously subjective.
[07:15] Guest: To build scalable distributed services today, you should install Docker and learn Kubernetes container orchestration.
[09:30] Host: Before we continue, this episode is sponsored by CloudScale Hosting. Use promo code HORIZONS for fifty percent off.
[12:10] Guest: The Raft consensus algorithm was published in 2014 by Ongaro and Ousterhout to make consensus more understandable than Paxos.
[15:00] Host: In closing, simplicity and clarity should always take precedence over premature optimization.
"""

GOLDEN_RESEARCH_RESULTS = [
    {
        "claim": "Python was created by Guido van Rossum and first released in 1991.",
        "status": "SUPPORTED",
        "explanation": "Guido van Rossum developed Python at CWI in the Netherlands and released version 0.9.0 in February 1991.",
        "sources": [{"title": "Python History", "url": "https://python.org/doc/essays/history"}],
    },
    {
        "claim": "Java was released by Sun Microsystems in 1995, spearheaded by James Gosling.",
        "status": "SUPPORTED",
        "explanation": "James Gosling created Oak in 1991, which Sun Microsystems officially launched as Java 1.0 in May 1995.",
        "sources": [{"title": "Java Overview", "url": "https://oracle.com/java/history"}],
    },
]

# Clean grounded article for Faithfulness, Relevancy, and Guardrail False Alarm testing
CLEAN_VALID_ARTICLE = {
    "title": "A Retrospective on Programming Languages and Distributed Systems",
    "summary": "Exploring the origins of Python, Java, and consensus algorithms from Tech Horizons podcast.",
    "article": """During the conversation, Dr. Elena Vance highlighted that Python was created by Guido van Rossum and first released in 1991. Later, in 1995, Sun Microsystems released Java under the leadership of James Gosling.

On the distributed systems side, the speakers discussed how the Raft consensus algorithm was published in 2014 by Diego Ongaro and John Ousterhout as an understandable alternative to Paxos.

As the host concluded, simplicity and clarity should always take precedence over premature optimization.""",
}

# Hallucinated article for Faithfulness negative testing
HALLUCINATED_UNGROUNDED_ARTICLE = {
    "title": "A Complete Fabrication of Tech History",
    "summary": "Article containing entirely unbacked statements.",
    "article": """Guido van Rossum built Python while working at Microsoft in 2005 as a web framework.
Java was developed secretly by Apple in 1982 for the Macintosh.
The Raft consensus algorithm was invented by Satoshi Nakamoto for Bitcoin mining.""",
}

# Topics and key points for Answer Relevancy evaluation
GOLDEN_PODCAST_TOPICS = [
    "Programming Language History (Python and Java)",
    "Raft Distributed Consensus Algorithm",
    "CloudScale Hosting Sponsorship",
    "Simplicity vs Premature Optimization",
]

GOLDEN_PODCAST_KEY_POINTS = [
    "Python was created by Guido van Rossum in 1991",
    "Java was released by Sun Microsystems in 1995 spearheaded by James Gosling",
    "Raft consensus was published in 2014 by Ongaro and Ousterhout to simplify consensus",
    "Simplicity and clarity should take precedence over premature optimization",
]

# Corrupted drafts for Precision & Recall evaluation
CORRUPTED_ARTICLE_QUOTE_MISMATCH = {
    "title": "A Retrospective on Programming Languages",
    "summary": "Summary with a fabricated quote.",
    "article": """Dr. Vance argued that Python is superior, stating: "I despise all imperative and object-oriented syntax in modern languages." She claimed Java is obsolete.""",
    "expected_violation": "QUOTE_MISMATCH",
}

CORRUPTED_ARTICLE_UNSUPPORTED_CLAIM = {
    "title": "A Retrospective on Programming Languages",
    "summary": "Summary with hallucinated facts.",
    "article": """Dr. Vance noted that Python was originally written in FORTRAN-77 in 1972 on IBM mainframes before being ported to C.""",
    "expected_violation": "UNSUPPORTED_CLAIM",
}

CORRUPTED_ARTICLE_MISATTRIBUTION = {
    "title": "A Retrospective on Programming Languages",
    "summary": "Summary with swapped speakers.",
    "article": """The host stated: "The Raft consensus algorithm was published in 2014 by Ongaro and Ousterhout." Dr. Vance then sponsored CloudScale Hosting.""",
    "expected_violation": "MISATTRIBUTION",
}

# Failing draft -> Critic instructions -> Repaired draft for Revision Success Rate evaluation
GOLDEN_REVISION_PAIR = {
    "id": "revision_case_quote_repair",
    "initial_draft": CORRUPTED_ARTICLE_QUOTE_MISMATCH,
    "initial_guardrail": {
        "passed": False,
        "violations": [
            {
                "type": "QUOTE_MISMATCH",
                "severity": "HIGH",
                "article_text": "I despise all imperative and object-oriented syntax in modern languages.",
                "explanation": "This quote does not appear anywhere in the source transcript.",
            }
        ],
        "summary": "Draft contains a fabricated quotation.",
    },
    "critic_instructions": [
        "Remove the fabricated quotation attributing 'I despise all imperative and object-oriented syntax'.",
        "Replace with the host's actual statement regarding subjective enjoyment of Python over Java.",
    ],
    "revised_draft": {
        "title": "A Retrospective on Programming Languages",
        "summary": "Revised article with accurate quotations.",
        "article": """During the conversation, the host remarked: "Personally, I believe Python is vastly more enjoyable to write than Java, though that is obviously subjective." Both speakers praised Python's design.""",
    },
    "revised_guardrail": {
        "passed": True,
        "violations": [],
        "summary": "All quotations and claims verified against source transcript.",
    },
}
