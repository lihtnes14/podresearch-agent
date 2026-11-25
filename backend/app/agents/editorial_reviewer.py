from langchain.agents import create_agent
from app.config import get_llm
from app.schemas import ArticleOutline, ArticleOutput, EditorialReviewOutput

EDITORIAL_REVIEWER_SYSTEM_PROMPT = """You are Agent 3: The YouTube Article Editorial Reviewer.

Your purpose is quality control. You review the article written by Agent 2 against the original transcript and Agent 1's structured outline.
You are an auditor and editor, NOT an article writer. Do not rewrite the article.

EVALUATION CRITERIA:
1. Transcript Grounding (Source of Truth):
   - Check whether claims in the article are supported by the original transcript.
   - Identify facts, commands, libraries, or explanations added without transcript support.
   - Distinguish between unsupported claims and technically incorrect claims. A statement might be true in general computing, but if the speaker never said it, note it as an unsupported claim without treating general knowledge as proof that the speaker mentioned it.
2. Outline & Concept Completeness:
   - Verify that all core concepts, sections, and important examples from Agent 1's outline are covered.
3. Timestamp Verification:
   - Verify that timestamps referenced in the article actually exist in the transcript and support the claimed point.
4. Technical Accuracy:
   - Check whether technical explanations have been distorted into inaccuracies.
5. Structure and Flow:
   - Identify repetitive or poorly structured prose.
6. Uncertainties Check:
   - Check whether uncertain facts flagged by Agent 1 are included in the section titled 'Uncertainties and Points to Verify'.

DECISION GUIDELINES:
- Set approved = True if the article is sufficiently accurate, grounded, complete, and readable. Minor stylistic issues or small helpful clarifications should NOT cause rejection.
- Set approved = False only if it contains critical factual hallucinations, severe distortions, or omits major sections.
- Always provide clear, encouraging feedback when approving, or actionable revision instructions when revision is recommended.
"""

_reviewer_agent_instance = None


def get_reviewer_agent():
    global _reviewer_agent_instance
    if _reviewer_agent_instance is None:
        _reviewer_agent_instance = create_agent(
            model=get_llm(),
            system_prompt=EDITORIAL_REVIEWER_SYSTEM_PROMPT,
            response_format=EditorialReviewOutput,
        )
    return _reviewer_agent_instance


def review_article(
    chunks: list[dict],
    outline: ArticleOutline,
    article: ArticleOutput,
) -> EditorialReviewOutput:
    """Invokes Agent 3 to review and audit the generated article."""
    formatted_transcript = []
    for chunk in chunks:
        header = f"--- Chunk {chunk.get('chunk_id')} ({chunk.get('start_timestamp')} to {chunk.get('end_timestamp')}) ---"
        lines = [f"[{seg.get('timestamp')}] {seg.get('text')}" for seg in chunk.get("segments", [])]
        formatted_transcript.append(header + "\n" + "\n".join(lines))

    full_transcript_str = "\n\n".join(formatted_transcript)

    audit_prompt = f"""Please conduct an editorial review of the following article against the outline and original transcript chunks:

=== ORIGINAL TRANSCRIPT CHUNKS (GROUND TRUTH) ===
{full_transcript_str}

=== AGENT 1 ARTICLE OUTLINE ===
{outline.model_dump_json(indent=2)}

=== AGENT 2 GENERATED ARTICLE ===
Title: {article.title}

{article.markdown_article}

Perform all checks and return your structured evaluation in the required JSON format.
"""

    agent = get_reviewer_agent()
    response = agent.invoke({
        "messages": [{"role": "user", "content": audit_prompt}]
    })

    if "structured_response" in response:
        return response["structured_response"]
    elif isinstance(response.get("messages", [])[-1].content, str):
        return EditorialReviewOutput.model_validate_json(response["messages"][-1].content)
    else:
        return EditorialReviewOutput.model_validate(response)
