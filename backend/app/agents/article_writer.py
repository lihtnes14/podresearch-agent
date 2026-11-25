import json
from typing import Optional, List
from langchain.agents import create_agent
from app.config import get_llm
from app.schemas import ArticleOutline, ArticleOutput

ARTICLE_WRITER_SYSTEM_PROMPT = """You are Agent 2: The YouTube Article Writer.

Your mission is to write a complete, engaging, publication-ready article based on the original YouTube transcript and the structured outline created by Agent 1.

RESPONSIBILITIES:
1. Follow the structure and section order defined in the article outline from Agent 1.
2. Write a comprehensive article featuring:
   - An engaging Title (# Title)
   - A well-crafted Introduction setting the context
   - Fully developed main sections with appropriate subheadings (## and ###)
   - Concrete code blocks (```bash or ```dockerfile) for all commands and technical examples
   - A dedicated section at the end titled '## Uncertainties and Points to Verify' explicitly covering any ambiguous points flagged by Agent 1 (e.g. uncertain release dates or versions)
   - A concise, thoughtful Conclusion summarizing key insights
   - The original YouTube video link referenced at the end
3. Convert spoken transcript explanations into clear, professional written prose.
4. Strip conversational filler words, greetings, like/subscribe requests, and repetitions.
5. Ground every technical explanation, command, and fact strictly in the transcript.
6. Embed original timestamps (e.g., `[02:15]`) within the relevant sections so readers can trace key concepts to the original video.
7. Ensure the article is entirely self-contained and clear to a reader who has not watched the video.

STRICT RULES:
- DO NOT invent facts, commands, libraries, or versions not present in the transcript.
- ALWAYS include '## Uncertainties and Points to Verify' before the conclusion if Agent 1 flagged any uncertainties.
- DO NOT copy the transcript verbatim; rephrase into smooth, authoritative writing.
- DO NOT output internal reasoning, apologies, or meta-comments.
- Output ONLY the final validated ArticleOutput containing the complete Markdown text.
"""

ARTICLE_REVISION_SYSTEM_PROMPT = """You are Agent 2: The YouTube Article Writer (Revision Mode).

Your mission is to revise the previous draft of the article based on Human Editorial Decisions and Agent 3 Review Feedback.

HUMAN-IN-THE-LOOP PRINCIPLES:
1. Human decisions take absolute priority over Agent 3's feedback.
2. If the human accepted an issue or requested a change, implement that modification cleanly.
3. If the human rejected an issue (e.g. electing to keep a technically accurate context explanation even if not in the video), keep that explanation intact!
4. Clearly distinguish transcript-supported content from additional technical context.
5. Ensure uncertain facts remain in the '## Uncertainties and Points to Verify' section.
6. Return the updated, publication-ready ArticleOutput in Markdown format.
"""

_writer_agent_instance = None
_reviser_agent_instance = None


def get_writer_agent():
    global _writer_agent_instance
    if _writer_agent_instance is None:
        _writer_agent_instance = create_agent(
            model=get_llm(),
            system_prompt=ARTICLE_WRITER_SYSTEM_PROMPT,
            response_format=ArticleOutput,
        )
    return _writer_agent_instance


def get_reviser_agent():
    global _reviser_agent_instance
    if _reviser_agent_instance is None:
        _reviser_agent_instance = create_agent(
            model=get_llm(),
            system_prompt=ARTICLE_REVISION_SYSTEM_PROMPT,
            response_format=ArticleOutput,
        )
    return _reviser_agent_instance


def write_article(
    video_title: str,
    chunks: list[dict],
    outline: ArticleOutline,
    video_url: str = "https://www.youtube.com/watch?v=sample",
    article_style: str = "technical, clear, and authoritative",
    target_audience: Optional[str] = None,
    video_description: Optional[str] = "",
) -> ArticleOutput:
    """Invokes Agent 2 to author the full Markdown article."""
    formatted_transcript = []
    for chunk in chunks:
        header = f"--- Chunk {chunk.get('chunk_id')} ({chunk.get('start_timestamp')} to {chunk.get('end_timestamp')}) ---"
        lines = [f"[{seg.get('timestamp')}] {seg.get('text')}" for seg in chunk.get("segments", [])]
        formatted_transcript.append(header + "\n" + "\n".join(lines))

    full_transcript_str = "\n\n".join(formatted_transcript)
    audience = target_audience or outline.target_audience

    user_prompt = f"""Write the full article using the following inputs:

=== VIDEO INFORMATION ===
Video Title: {video_title}
Video URL: {video_url}
Video Description: {video_description or 'N/A'}
Target Audience: {audience}
Desired Style: {article_style}

=== ARTICLE OUTLINE FROM AGENT 1 ===
{outline.model_dump_json(indent=2)}

=== ORIGINAL TRANSCRIPT CHUNKS (GROUND TRUTH) ===
{full_transcript_str}

Produce the complete, polished Markdown article following the outline and instructions.
"""

    agent = get_writer_agent()
    response = agent.invoke({
        "messages": [{"role": "user", "content": user_prompt}]
    })

    if "structured_response" in response:
        return response["structured_response"]
    elif isinstance(response.get("messages", [])[-1].content, str):
        return ArticleOutput.model_validate_json(response["messages"][-1].content)
    else:
        return ArticleOutput.model_validate(response)


def revise_article(
    previous_article_markdown: str,
    human_instructions: str,
    accepted_feedback: List[str],
    chunks: list[dict],
    outline: ArticleOutline,
) -> ArticleOutput:
    """Revises the article incorporating accepted human editorial feedback."""
    formatted_transcript = []
    for chunk in chunks:
        header = f"--- Chunk {chunk.get('chunk_id')} ({chunk.get('start_timestamp')} to {chunk.get('end_timestamp')}) ---"
        lines = [f"[{seg.get('timestamp')}] {seg.get('text')}" for seg in chunk.get("segments", [])]
        formatted_transcript.append(header + "\n" + "\n".join(lines))

    full_transcript_str = "\n\n".join(formatted_transcript)

    revision_prompt = f"""Revise the article according to the human editor's instructions:

=== PREVIOUS ARTICLE DRAFT ===
{previous_article_markdown}

=== ACCEPTED EDITORIAL ISSUES & INSTRUCTIONS ===
{json.dumps(accepted_feedback, indent=2)}

=== DIRECT HUMAN INSTRUCTIONS ===
{human_instructions or 'Apply all accepted editorial corrections cleanly.'}

=== ORIGINAL TRANSCRIPT CHUNKS (GROUND TRUTH) ===
{full_transcript_str}

Produce the revised, polished Markdown article.
"""

    agent = get_reviser_agent()
    response = agent.invoke({
        "messages": [{"role": "user", "content": revision_prompt}]
    })

    if "structured_response" in response:
        return response["structured_response"]
    elif isinstance(response.get("messages", [])[-1].content, str):
        return ArticleOutput.model_validate_json(response["messages"][-1].content)
    else:
        return ArticleOutput.model_validate(response)
