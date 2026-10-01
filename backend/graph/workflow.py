import json

from langgraph.graph import StateGraph, START, END

from graph.state import PodcastState

from agents.transcript_agent import get_transcript
from agents.analysis_agent import analyze_transcript
from agents.research_agent import research_claims
from agents.writer_agent import write_article
from agents.guardrail_agent import check_article
from agents.critic_agent import critique_article

from memory.session_memory import (
    save_artifact,
    update_session,
    get_latest_artifact,
)

from agents.memory_agent import (
    retrieve_relevant_memory,
    store_research_memory,
)

def load_memory_node(state: PodcastState):
    print()
    print("🧠 LOADING SESSION MEMORY")
    print()

    session_id = state["session_id"]

    loaded_artifacts = []
    loaded_state = {}

    artifact_types = [
        "transcript",
        "analysis",
        "research",
        "article",
        "guardrail",
        "critique",
    ]

    for artifact_type in artifact_types:

        artifact = get_latest_artifact(
            session_id=session_id,
            artifact_type=artifact_type
        )

        if artifact is None:
            continue

        print(f"  ✓ Loaded {artifact_type}")

        loaded_artifacts.append(artifact_type)

        content = artifact.content

        if artifact_type == "transcript":
            loaded_state["transcript"] = content

        elif artifact_type == "analysis":
            loaded_state["analysis"] = json.loads(content)

        elif artifact_type == "research":
            loaded_state["research"] = json.loads(content)

        elif artifact_type == "article":
            loaded_state["article"] = json.loads(content)

        elif artifact_type == "guardrail":
            loaded_state["guardrail_result"] = json.loads(content)

        elif artifact_type == "critique":
            loaded_state["critique"] = json.loads(content)

    loaded_state["loaded_artifacts"] = loaded_artifacts

    return loaded_state


def transcript_node(state: PodcastState):
    print()
    print("🎙️ TRANSCRIPT AGENT")
    print()

    transcript = get_transcript(state["podcast_url"])

    save_artifact(
        session_id=state["session_id"],
        artifact_type="transcript",
        content=transcript
    )

    return {
        "transcript": transcript
    }


def analysis_node(state: PodcastState):
    print()
    print("🧠 ANALYSIS AGENT")
    print()

    analysis = analyze_transcript(
        state["transcript"]
    )

    save_artifact(
        session_id=state["session_id"],
        artifact_type="analysis",
        content=json.dumps(
            analysis,
            indent=2
        )
    )

    return {
        "analysis": analysis
    }


def research_node(state: PodcastState):

    research = research_claims(
        claims=state["analysis"]["claims"],
        historical_context=state.get(
            "historical_context",
            []
        ),
    )

    save_artifact(
        state["session_id"],
        "research",
        json.dumps(research)
    )

    store_research_memory(
        session_id=state["session_id"],
        research=research,
    )

    revision_count = state.get("revision_count", 0)

    # If an article already exists, this research run
    # is a repair cycle triggered by the guardrail.
    if state.get("article"):
        revision_count += 1

    return {
        "research": research,
        "revision_count": revision_count
    }


def writer_node(state: PodcastState):
    print()
    print("✍️ WRITER AGENT")
    print()

    critique = state.get("critique")

    article = write_article(
        transcript=state["transcript"],
        analysis=state["analysis"],
        research=state["research"],
        critique=critique
    )


    save_artifact(
        session_id=state["session_id"],
        artifact_type="article",
        content=json.dumps(
            article,
            indent=2
        )
    )

    return {
        "article": article
    }


def guardrail_node(state: PodcastState):
    print()
    print("🛡️ GUARDRAIL AGENT")
    print()

    guardrail_result = check_article(
        transcript=state["transcript"],
        research=state["research"],
        article=state["article"]
    )

    save_artifact(
        session_id=state["session_id"],
        artifact_type="guardrail",
        content=json.dumps(
            guardrail_result,
            indent=2
        )
    )

    return {
        "guardrail_result": guardrail_result
    }


def critic_node(state: PodcastState):
    print()
    print("🧐 CRITIC AGENT")
    print()

    critique = critique_article(
        article=state["article"],
        guardrail_result=state["guardrail_result"]
    )

    save_artifact(
        session_id=state["session_id"],
        artifact_type="critique",
        content=json.dumps(
            critique,
            indent=2
        )
    )

    return {
        "critique": critique,
        "revision_count": state["revision_count"] + 1
    }


def route_after_memory(state: PodcastState):

    loaded = state["loaded_artifacts"]

    if "transcript" not in loaded:
        return "transcript"

    if "analysis" not in loaded:
        return "analysis"

    if "research" not in loaded:
        return "memory_retrieval"

    if "article" not in loaded:
        return "writer"

    if "guardrail" not in loaded:
        return "guardrail"

    return "end"


def route_after_guardrail(state: PodcastState):

    guardrail_result = state["guardrail_result"]

    if guardrail_result["passed"]:

        print()
        print("✅ GUARDRAIL PASSED")
        print()

        update_session(
            state["session_id"],
            status="article_ready"
        )

        return "end"

    if state["revision_count"] >= 2:

        print()
        print("❌ MAXIMUM REVISIONS REACHED")
        print()

        update_session(
            state["session_id"],
            status="guardrail_failed"
        )

        return "end"

    violations = guardrail_result.get(
        "violations",
        []
    )

    evidence_issue_types = {
        "UNSUPPORTED_CLAIM",
        "HALLUCINATION",
    }

    has_evidence_issue = any(
        violation["type"] in evidence_issue_types
        for violation in violations
    )

    if has_evidence_issue:

        print()
        print("⚠️ GUARDRAIL FAILED → RESEARCH")
        print()

        return "research"

    print()
    print("⚠️ GUARDRAIL FAILED → CRITIC")
    print()

    return "critic"

def memory_retrieval_node(state: PodcastState):

    analysis = state["analysis"]

    topics = analysis.get("topics", [])
    claims = analysis.get("claims", [])

    query_parts = []

    query_parts.extend(topics)

    for claim in claims:
        query_parts.append(claim["claim"])

    query = " ".join(query_parts)

    memories = retrieve_relevant_memory(
        query=query,
        current_session_id=state["session_id"],
        n_results=3,
    )

    print("\n🧠 SEMANTIC MEMORY")
    print(f"Retrieved {len(memories)} historical memories")

    for memory in memories:
        print(
            f"  → {memory['metadata'].get('topic')} "
            f"(session: {memory['metadata'].get('session_id')})"
        )

    return {
        "historical_context": memories
    }

def build_graph():

    graph = StateGraph(PodcastState)

    graph.add_node(
        "memory",
        load_memory_node
    )

    graph.add_node(
        "transcript",
        transcript_node
    )

    graph.add_node(
        "analysis",
        analysis_node
    )

    graph.add_node(
    "memory_retrieval",
    memory_retrieval_node
)

    graph.add_node(
        "research",
        research_node
    )

    graph.add_node(
        "writer",
        writer_node
    )

    graph.add_node(
        "guardrail",
        guardrail_node
    )

    graph.add_node(
        "critic",
        critic_node
    )



    # START
    graph.add_edge(
        START,
        "memory"
    )

    # Memory decides whether transcript needs to be created
    graph.add_conditional_edges(
    "memory",
    route_after_memory,
    {
    "transcript": "transcript",
    "analysis": "analysis",
    "memory_retrieval": "memory_retrieval",
    "writer": "writer",
    "guardrail": "guardrail",
    "end": END
}
)

    # Normal pipeline
    graph.add_edge(
        "transcript",
        "analysis"
    )

    graph.add_edge("analysis", "memory_retrieval")
    graph.add_edge("memory_retrieval", "research")

    graph.add_edge(
        "research",
        "writer"
    )

    graph.add_edge(
        "writer",
        "guardrail"
    )

    # Guardrail loop
    graph.add_conditional_edges(
    "guardrail",
    route_after_guardrail,
    {
        "critic": "critic",
        "research": "research",
        "end": END
    }
)

    graph.add_edge(
        "critic",
        "writer"
    )

    return graph.compile()


workflow = build_graph()