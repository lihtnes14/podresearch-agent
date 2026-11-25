# 🎙️ PodResearch Agent

An autonomous multi-agent research and journalism pipeline built with **LangGraph**, **FastAPI**, **Azure OpenAI**, **Tavily Search**, **SQLite**, and **ChromaDB**.

PodResearch Agent accepts a YouTube podcast URL, segments and transcribes the episode, extracts factual claims, cross-references historical memory, conducts web research, drafts an evidence-backed article, evaluates it against strict guardrails, and self-corrects with an autonomous critic feedback loop.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)

Ensure your `.env` contains:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_DEPLOYMENT=gpt-4o-or-similar

TAVILY_API_KEY=tvly-your_key

LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=podresearch-agent
```

---

## ⚡ Running the FastAPI Backend

Start the FastAPI backend with Uvicorn:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

* **Interactive OpenAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 💻 Running the Streamlit Frontend

Run the Streamlit app:

```bash
streamlit run frontend/app.py
```

* If the FastAPI server is running on `http://localhost:8000`, the frontend automatically connects over REST and streams live workflow execution events via Server-Sent Events (SSE).
* If FastAPI is not running, Streamlit gracefully falls back to local direct execution.

---

## 📡 API Endpoints

### Health
- `GET /health` — Service health check.

### Sessions
- `POST /api/sessions` — Create a new session (`title`, `podcast_url`).
- `GET /api/sessions` — List all sessions.
- `GET /api/sessions/{session_id}` — Get session details and all associated artifacts.
- `PATCH /api/sessions/{session_id}` — Update session title or status.
- `DELETE /api/sessions/{session_id}` — Delete a session and its artifacts.

### Artifacts
- `GET /api/sessions/{session_id}/artifacts` — List all artifacts for a session.
- `GET /api/sessions/{session_id}/artifacts/{artifact_type}` — Retrieve the latest artifact (`article`, `guardrail`, `analysis`, `research`, `transcript`).

### Workflow Execution
- `POST /api/sessions/{session_id}/run` — Run the research workflow synchronously.
- `GET /api/sessions/{session_id}/stream` — Stream live workflow execution events via **Server-Sent Events (SSE)**.

---

## 🧪 Testing & Agentic Evaluations

### Run All Tests & Evals with Pytest
```bash
python -m pytest tests/ evals/ -v
```

### Run Standalone Evaluation Scorecard
```bash
python -m evals.runner
```

### Run DeepEval Framework Suite
```bash
python -m evals.deepeval_suite
```

Runs the multi-metric evaluation harness and generates a detailed scorecard covering:

| Target Metric | Evaluation Purpose | Target |
| :--- | :--- | :--- |
| **Faithfulness** | Factual grounding of generated articles against transcript and research | $\ge 85\%$ |
| **Answer Relevancy** | Alignment with core podcast topics and key discussion points | $\ge 80\%$ |
| **Revision Success Rate** | Effectiveness of the Critic–Writer self-correction loop | $\ge 80\%$ |
| **Precision** | Correctness of guardrail flags (zero false alarms on clean articles) | $\ge 85\%$ |
| **Recall** | Ability to catch actual injected violations in corrupted drafts | $\ge 85\%$ |
| **End-to-End Latency** | Pipeline and node performance against operational SLAs | $\ge 85\%$ |



