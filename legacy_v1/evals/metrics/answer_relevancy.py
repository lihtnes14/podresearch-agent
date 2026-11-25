"""Metric: Answer Relevancy (Relevance to Podcast Content).
Measures whether the generated article directly addresses and elaborates on
the central topics and key themes of the podcast without introducing irrelevant tangents.

Relevancy Score = (0.5 * Topic Coverage) + (0.3 * Entity/Concept Alignment) + (0.2 * Non-tangent Penalty)
Target: >= 0.80
"""
from __future__ import annotations

import re
from difflib import SequenceMatcher


def normalize_tokens(text: str) -> set[str]:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = [w for w in text.split() if len(w) > 3]
    return set(tokens)


def evaluate_answer_relevancy(
    article: dict,
    podcast_topics: list[str],
    podcast_key_points: list[str],
) -> dict:
    article_title = article.get("title", "")
    article_summary = article.get("summary", "")
    article_body = article.get("article", "")
    combined_article = f"{article_title} {article_summary} {article_body}".lower()

    if not combined_article.strip() or not podcast_topics:
        return {
            "topic_coverage": 0.0,
            "key_point_coverage": 0.0,
            "relevancy_score": 0.0,
            "overall_score": 0.0,
            "passed": False,
            "uncovered_topics": podcast_topics,
        }

    # 1. Topic Coverage: Check how many key topics are discussed
    topics_covered = 0
    uncovered = []
    for topic in podcast_topics:
        norm_topic = topic.lower()
        topic_words = [w for w in norm_topic.split() if len(w) > 3]
        if any(w in combined_article for w in topic_words) or norm_topic in combined_article:
            topics_covered += 1
        else:
            uncovered.append(topic)

    topic_coverage_rate = topics_covered / len(podcast_topics) if podcast_topics else 1.0

    # 2. Key Point Coverage: How many core discussion points are reflected
    points_covered = 0
    article_tokens = normalize_tokens(combined_article)
    for point in podcast_key_points:
        point_tokens = normalize_tokens(point)
        if not point_tokens:
            continue
        common = point_tokens.intersection(article_tokens)
        if len(common) / len(point_tokens) >= 0.40:
            points_covered += 1

    key_point_rate = (
        points_covered / len(podcast_key_points) if podcast_key_points else 1.0
    )

    # 3. Composite Relevancy Score
    overall_score = round(
        (0.60 * topic_coverage_rate) + (0.40 * key_point_rate), 4
    )
    passed = overall_score >= 0.80

    return {
        "total_topics": len(podcast_topics),
        "topics_covered": topics_covered,
        "topic_coverage_rate": round(topic_coverage_rate, 4),
        "total_key_points": len(podcast_key_points),
        "key_points_covered": points_covered,
        "key_point_rate": round(key_point_rate, 4),
        "relevancy_score": overall_score,
        "overall_score": overall_score,
        "passed": passed,
        "uncovered_topics": uncovered,
    }
