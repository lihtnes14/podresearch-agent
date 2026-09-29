import json

import streamlit as st

from memory.session_memory import (
    create_session,
    list_sessions,
    get_latest_artifact,
)

from graph.workflow import workflow


# =========================================================
# HELPERS
# =========================================================

def load_json_artifact(artifact):
    if artifact is None:
        return None

    try:
        return json.loads(artifact.content)

    except json.JSONDecodeError:
        return None


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="PodResearch Agent",
    page_icon="🎙️",
    layout="wide",
)


# =========================================================
# SESSION STATE
# =========================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "final_state" not in st.session_state:
    st.session_state.final_state = None


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🎙️ PodResearch Agent")

st.sidebar.subheader("Sessions")

sessions = list_sessions()

for session_item in sessions:

    label = session_item.title

    if st.sidebar.button(
        label,
        key=f"session_{session_item.id}",
    ):
        st.session_state.session_id = session_item.id
        st.session_state.final_state = None
        st.rerun()


st.sidebar.divider()

if st.sidebar.button("➕ New Session"):

    st.session_state.session_id = None
    st.session_state.final_state = None

    st.rerun()


# =========================================================
# NEW SESSION
# =========================================================

if st.session_state.session_id is None:

    st.title("🎙️ PodResearch Agent")

    st.write(
        "Turn a podcast into a researched, evidence-backed article "
        "using a multi-agent workflow."
    )

    podcast_url = st.text_input(
        "Podcast / YouTube URL",
        placeholder="https://youtube.com/...",
    )

    title = st.text_input(
        "Session title",
        placeholder="My Podcast Research",
    )

    if st.button(
        "🚀 Start Research",
        type="primary",
    ):

        if not podcast_url:

            st.warning(
                "Please enter a podcast URL."
            )

        elif not title:

            st.warning(
                "Please enter a session title."
            )

        else:

            session = create_session(
                title=title,
                podcast_url=podcast_url,
            )

            st.session_state.session_id = session.id
            st.session_state.final_state = None

            st.rerun()

    st.stop()


# =========================================================
# LOAD CURRENT SESSION
# =========================================================

session_id = st.session_state.session_id

session = next(
    (
        s
        for s in sessions
        if s.id == session_id
    ),
    None,
)


if session is None:

    st.error("Session not found.")

    st.session_state.session_id = None
    st.session_state.final_state = None

    st.stop()


# =========================================================
# SESSION HEADER
# =========================================================

st.title(
    f"🎙️ {session.title}"
)

st.caption(
    f"Session ID: {session.id}"
)

st.write(
    f"**Podcast:** {session.podcast_url}"
)


# =========================================================
# RUN WORKFLOW
# =========================================================

st.divider()

if st.button(
    "🚀 Run PodResearch Agent",
    type="primary",
):

    initial_state = {
        "session_id": session.id,
        "podcast_url": session.podcast_url,

        "transcript": "",
        "analysis": {},
        "research": [],

        "article": {},
        "guardrail_result": {},
        "critique": {},

        "revision_count": 0,

        "loaded_artifacts": [],
    }

    final_state = initial_state.copy()

    # -----------------------------------------------------
    # AGENT STATUS
    # -----------------------------------------------------

    status = st.status(
        "🚀 Starting PodResearch Agent...",
        expanded=True,
    )

    # -----------------------------------------------------
    # NODE DISPLAY NAMES
    # -----------------------------------------------------

    node_names = {

        "memory":
            "🧠 Memory",

        "transcript":
            "🎙️ Transcript Agent",

        "analysis":
            "🧠 Analysis Agent",

        "research":
            "🔎 Research Agent",

        "writer":
            "✍️ Writer Agent",

        "guardrail":
            "🛡️ Guardrail Agent",

        "critic":
            "🧐 Critic Agent",
    }

    try:

        # -------------------------------------------------
        # STREAM LANGGRAPH EXECUTION
        # -------------------------------------------------

        for event in workflow.stream(
            initial_state
        ):

            for node_name, state_update in event.items():

                # Keep track of the complete state
                final_state.update(
                    state_update
                )

                display_name = node_names.get(
                    node_name,
                    node_name,
                )

                # =========================================
                # MEMORY
                # =========================================

                if node_name == "memory":

                    loaded_artifacts = (
                        state_update.get(
                            "loaded_artifacts",
                            [],
                        )
                    )

                    if loaded_artifacts:

                        status.write(
                            f"🧠 **Memory** — "
                            f"Loaded "
                            f"{len(loaded_artifacts)} "
                            f"artifact(s)"
                        )

                        for artifact_type in loaded_artifacts:

                            status.write(
                                f"   ✓ {artifact_type}"
                            )

                    else:

                        status.write(
                            "🧠 **Memory** — "
                            "No previous artifacts found"
                        )

                # =========================================
                # TRANSCRIPT
                # =========================================

                elif node_name == "transcript":

                    status.write(
                        "🎙️ **Transcript Agent** — "
                        "Transcript generated"
                    )

                # =========================================
                # ANALYSIS
                # =========================================

                elif node_name == "analysis":

                    analysis_data = (
                        state_update.get(
                            "analysis",
                            {},
                        )
                    )

                    claims = (
                        analysis_data.get(
                            "claims",
                            [],
                        )
                    )

                    topics = (
                        analysis_data.get(
                            "topics",
                            [],
                        )
                    )

                    status.write(
                        f"🧠 **Analysis Agent** — "
                        f"{len(topics)} topics, "
                        f"{len(claims)} claims detected"
                    )

                # =========================================
                # RESEARCH
                # =========================================

                elif node_name == "research":

                    research_data = (
                        state_update.get(
                            "research",
                            [],
                        )
                    )

                    status.write(
                        f"🔎 **Research Agent** — "
                        f"{len(research_data)} claims researched"
                    )

                # =========================================
                # WRITER
                # =========================================

                elif node_name == "writer":

                    revision_count = (
                        final_state.get(
                            "revision_count",
                            0,
                        )
                    )

                    if revision_count > 0:

                        status.write(
                            f"✍️ **Writer Agent** — "
                            f"Article revised "
                            f"(revision {revision_count})"
                        )

                    else:

                        status.write(
                            "✍️ **Writer Agent** — "
                            "Article generated"
                        )

                # =========================================
                # GUARDRAIL
                # =========================================

                elif node_name == "guardrail":

                    guardrail_data = (
                        state_update.get(
                            "guardrail_result",
                            {},
                        )
                    )

                    passed = (
                        guardrail_data.get(
                            "passed",
                            False,
                        )
                    )

                    violations = (
                        guardrail_data.get(
                            "violations",
                            [],
                        )
                    )

                    if passed:

                        status.write(
                            "🛡️ **Guardrail Agent** — "
                            "✅ All checks passed"
                        )

                    else:

                        status.write(
                            f"🛡️ **Guardrail Agent** — "
                            f"❌ {len(violations)} "
                            f"violation(s) detected"
                        )

                # =========================================
                # CRITIC
                # =========================================

                elif node_name == "critic":

                    revision_count = (
                        state_update.get(
                            "revision_count",
                            0,
                        )
                    )

                    status.write(
                        f"🧐 **Critic Agent** — "
                        f"Revision {revision_count}"
                    )

        # -------------------------------------------------
        # COMPLETE
        # -------------------------------------------------

        status.update(
            label="✅ PodResearch Agent completed",
            state="complete",
            expanded=False,
        )

        st.session_state.final_state = final_state

        st.success(
            "PodResearch workflow completed."
        )

    except Exception as e:

        status.update(
            label="❌ Workflow failed",
            state="error",
            expanded=True,
        )

        st.error(
            f"Workflow error: {str(e)}"
        )


# =========================================================
# LOAD ARTIFACTS FROM MEMORY
# =========================================================

article = get_latest_artifact(
    session_id,
    "article",
)

guardrail = get_latest_artifact(
    session_id,
    "guardrail",
)

analysis = get_latest_artifact(
    session_id,
    "analysis",
)

research = get_latest_artifact(
    session_id,
    "research",
)

transcript = get_latest_artifact(
    session_id,
    "transcript",
)


# =========================================================
# FINAL ARTICLE
# =========================================================

if article is not None:

    article_data = load_json_artifact(
        article
    )

    if article_data is not None:

        st.divider()

        st.header(
            article_data.get(
                "title",
                "Untitled Article",
            )
        )

        st.subheader(
            "Summary"
        )

        st.write(
            article_data.get(
                "summary",
                "",
            )
        )

        st.subheader(
            "Article"
        )

        st.markdown(
            article_data.get(
                "article",
                "",
            )
        )

    else:

        st.warning(
            "The saved article artifact could not be parsed."
        )


# =========================================================
# GUARDRAILS
# =========================================================

if guardrail is not None:

    guardrail_data = load_json_artifact(
        guardrail
    )

    if guardrail_data is not None:

        st.divider()

        st.subheader(
            "🛡️ Guardrail Results"
        )

        if guardrail_data.get(
            "passed",
            False,
        ):

            st.success(
                "All guardrails passed."
            )

        else:

            st.error(
                "Guardrails detected violations."
            )

        st.write(
            guardrail_data.get(
                "summary",
                "",
            )
        )

        violations = (
            guardrail_data.get(
                "violations",
                [],
            )
        )

        if violations:

            for violation in violations:

                st.warning(
                    f"{violation.get('type', 'UNKNOWN')} — "
                    f"{violation.get('severity', 'UNKNOWN')}"
                )

                st.write(
                    violation.get(
                        "explanation",
                        "",
                    )
                )

    else:

        st.warning(
            "The saved guardrail artifact "
            "could not be parsed."
        )


# =========================================================
# ANALYSIS
# =========================================================

if analysis is not None:

    analysis_data = load_json_artifact(
        analysis
    )

    if analysis_data is not None:

        with st.expander(
            "🧠 Podcast Analysis"
        ):

            # ---------------------------------------------
            # TOPICS
            # ---------------------------------------------

            st.subheader(
                "Topics"
            )

            topics = analysis_data.get(
                "topics",
                [],
            )

            for topic in topics:

                st.write(
                    f"- {topic}"
                )

            # ---------------------------------------------
            # CLAIMS
            # ---------------------------------------------

            st.subheader(
                "Claims"
            )

            claims = analysis_data.get(
                "claims",
                [],
            )

            for claim in claims:

                st.write(
                    f"**{claim.get('claim', '')}**"
                )

                st.caption(
                    f"Speaker: "
                    f"{claim.get('speaker', 'Unknown')} | "
                    f"Timestamp: "
                    f"{claim.get('timestamp', 'Unknown')}"
                )

            # ---------------------------------------------
            # QUOTES
            # ---------------------------------------------

            quotes = analysis_data.get(
                "quotes",
                [],
            )

            if quotes:

                st.subheader(
                    "Quotes"
                )

                for quote in quotes:

                    st.write(
                        f"“{quote.get('quote', '')}”"
                    )

                    st.caption(
                        f"Speaker: "
                        f"{quote.get('speaker', 'Unknown')} | "
                        f"Timestamp: "
                        f"{quote.get('timestamp', 'Unknown')}"
                    )

            # ---------------------------------------------
            # AGREEMENTS
            # ---------------------------------------------

            agreements = analysis_data.get(
                "agreements",
                [],
            )

            if agreements:

                st.subheader(
                    "Agreements"
                )

                for agreement in agreements:

                    st.write(
                        f"- {agreement}"
                    )

            # ---------------------------------------------
            # DISAGREEMENTS
            # ---------------------------------------------

            disagreements = analysis_data.get(
                "disagreements",
                [],
            )

            if disagreements:

                st.subheader(
                    "Disagreements"
                )

                for disagreement in disagreements:

                    st.write(
                        f"- {disagreement}"
                    )

    else:

        st.warning(
            "The saved analysis artifact is from "
            "an older or invalid format. "
            "Run the workflow again to regenerate it."
        )


# =========================================================
# RESEARCH
# =========================================================

if research is not None:

    research_data = load_json_artifact(
        research
    )

    if research_data is not None:

        with st.expander(
            "🔎 Research Results"
        ):

            for result in research_data:

                status_value = result.get(
                    "status",
                    "UNKNOWN",
                )

                st.write(
                    f"### {status_value}"
                )

                st.write(
                    result.get(
                        "claim",
                        "",
                    )
                )

                st.write(
                    result.get(
                        "explanation",
                        "",
                    )
                )

                sources = result.get(
                    "sources",
                    [],
                )

                if sources:

                    st.write(
                        "**Sources:**"
                    )

                    for source in sources:

                        title = source.get(
                            "title",
                            "Untitled source",
                        )

                        url = source.get(
                            "url",
                            "",
                        )

                        if url:

                            st.markdown(
                                f"- [{title}]({url})"
                            )

                        else:

                            st.write(
                                f"- {title}"
                            )

    else:

        st.warning(
            "The saved research artifact "
            "could not be parsed."
        )


# =========================================================
# TRANSCRIPT
# =========================================================

if transcript is not None:

    with st.expander(
        "🎙️ Transcript"
    ):

        st.text(
            transcript.content
        )