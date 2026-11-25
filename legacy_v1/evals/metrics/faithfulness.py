"""Metric: Faithfulness (Factual Grounding of Generated Articles).
Measures the proportion of factual statements made in the generated article
that are directly grounded in the verified source transcript and external research findings.

Faithfulness Score = (Grounded Claims in Article) / (Total Factual Claims in Article)
Target: >= 0.85 (High factual fidelity, zero or minimal hallucinations)
"""
from __future__ import annotations

import re
from difflib import SequenceMatcher


def extract_sentences(text: str) -> list[str]:
    """Split article text into clean distinct statements/sentences without breaking on honorifics like Dr., Mr."""
    # Protect honorifics/titles
    protected = re.sub(r"\b(Dr|Mr|Mrs|Ms|Prof|Sr|Jr)\.", r"\1<DOT>", text)
    raw_sentences = re.split(r"(?<=[.!?])\s+", protected)
    cleaned = []
    for s in raw_sentences:
        s_unmasked = s.replace("<DOT>", ".").strip()
        # Filter out headers, titles, or very short snippets
        if len(s_unmasked) > 20 and not s_unmasked.startswith("#"):
            cleaned.append(s_unmasked)
    return cleaned


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r'["\'`“”‘’]', "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def is_claim_grounded(
    claim_sentence: str,
    context_corpus: str,
    keywords_threshold: float = 0.60,
) -> bool:
    """Determine if a sentence from the article is grounded in the transcript/research corpus."""
    norm_claim = normalize(claim_sentence)
    norm_corpus = normalize(context_corpus)

    # 1. Exact or near substring match
    if norm_claim in norm_corpus:
        return True

    # 2. Key entity / keyword overlap
    words = [w for w in norm_claim.split() if len(w) > 3]
    if not words:
        return True

    matching_words = [w for w in words if w in norm_corpus]
    overlap_ratio = len(matching_words) / len(words)

    # 3. Fuzzy sequence matcher on sentences
    best_sim = 0.0
    corpus_sentences = extract_sentences(context_corpus)
    for c_sent in corpus_sentences:
        sim = SequenceMatcher(None, norm_claim, normalize(c_sent)).ratio()
        if sim > best_sim:
            best_sim = sim

    return (overlap_ratio >= keywords_threshold) or (best_sim >= 0.65)


def evaluate_faithfulness(
    article: dict,
    raw_transcript: str,
    verified_research: list[dict],
) -> dict:
    article_body = article.get("article", "")
    if not article_body:
        return {
            "total_statements": 0,
            "grounded_statements": 0,
            "ungrounded_statements": 0,
            "faithfulness_score": 0.0,
            "passed": False,
            "ungrounded_claims": [],
        }

    # Aggregate all ground-truth evidence corpus
    research_text = " ".join(
        f"{r.get('claim', '')} {r.get('explanation', '')}"
        for r in verified_research
    )
    evidence_corpus = f"{raw_transcript} {research_text}"

    sentences = extract_sentences(article_body)
    grounded_count = 0
    ungrounded = []

    for sentence in sentences:
        if is_claim_grounded(sentence, evidence_corpus):
            grounded_count += 1
        else:
            ungrounded.append(sentence)

    total = len(sentences)
    score = round(grounded_count / total, 4) if total > 0 else 1.0
    passed = score >= 0.85

    return {
        "total_statements": total,
        "grounded_statements": grounded_count,
        "ungrounded_statements": len(ungrounded),
        "faithfulness_score": score,
        "overall_score": score,
        "passed": passed,
        "ungrounded_claims": ungrounded[:5],
    }
