from langchain.agents import create_agent
from app.config import get_llm
from app.schemas import ArticleOutline

CONTENT_ANALYST_SYSTEM_PROMPT = """You are Agent 1: The YouTube Content Analyst.

Your job is to read all transcript chunks from a YouTube video and create a structured, publication-ready article outline for the writer agent.

GUIDELINES:
1. Understand the core topic and formulate an appealing, informative article title.
2. Determine the target audience and primary takeaways.
3. Group the material logically by theme into coherent sections. Do NOT create one section per chunk; organize by topic.
4. Remove fluff: ignore channel intros, subscription requests, greetings, and filler chatter.
5. Preserve original timestamps for every section so the writer can ground every point.
6. Retain important examples, commands, analogies, and technical details.
7. Note any uncertainties or ambiguous statements so the writer does not make false assumptions.
8. DO NOT write the article body yet. Output ONLY the structured outline.
"""

# Lazy-loaded agent graph
_agent_instance = None


def get_analyst_agent():
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = create_agent(
            model=get_llm(),
            system_prompt=CONTENT_ANALYST_SYSTEM_PROMPT,
            response_format=ArticleOutline,
        )
    return _agent_instance


def generate_article_outline(chunks: list[dict]) -> ArticleOutline:
    """Takes transcript chunks and executes Agent 1 to generate the article outline."""
    formatted_blocks = []
    for chunk in chunks:
        header = f"--- Chunk {chunk.get('chunk_id')} ({chunk.get('start_timestamp')} to {chunk.get('end_timestamp')}) ---"
        lines = [f"[{seg.get('timestamp')}] {seg.get('text')}" for seg in chunk.get("segments", [])]
        formatted_blocks.append(header + "\n" + "\n".join(lines))

    full_transcript_str = "\n\n".join(formatted_blocks)

    user_prompt = f"""Here are the transcript chunks from the video:

{full_transcript_str}

Analyze these chunks and generate the structured article outline.
"""

    agent = get_analyst_agent()
    response = agent.invoke({
        "messages": [{"role": "user", "content": user_prompt}]
    })

    if "structured_response" in response:
        return response["structured_response"]
    elif isinstance(response.get("messages", [])[-1].content, str):
        return ArticleOutline.model_validate_json(response["messages"][-1].content)
    else:
        return ArticleOutline.model_validate(response)
