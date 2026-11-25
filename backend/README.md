# 🎙️ PodResearch 2.0

Autonomous Multi-Agent YouTube Article Generator with **LangChain**, **LangGraph**, **FastAPI**, and **Human-in-the-Loop (HITL) Review**.

---

## 🏗️ Architecture & Workflow

```text
YouTube URL
    │
    ▼
[Transcript Extraction & Chunking] (300s time slices)
    │
    ▼
[Agent 1: YouTube Content Analyst]
    │  - Semantic Topic Synthesis & Key Takeaways
    │  - Structured Outline & Timestamp Tracking
    │  - Flagged Uncertainties
    ▼
[Agent 2: YouTube Article Writer]
    │  - Written Prose Conversion
    │  - Code Blocks & Section Formatting
    │  - Grounded Strictly in Transcript
    ▼
[Agent 3: YouTube Article Editorial Reviewer]
    │  - Hallucination & Distorted Fact Detection
    │  - Timestamp Provenance Verification
    │  - Uncertainties Section Validation
    ▼
[Human-in-the-Loop Review Stage] ◄────► [Agent 2 Revision Loop]
    │  - Accept / Reject Individual Suggestions
    │  - Direct Markdown Editing
    │  - Version Comparison
    ▼
[Official Publication Approval Certificate]
```

---

## 📂 Project Structure

```text
pod_research_2/
├── run.py                 # FastAPI server runner
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Build metadata
├── .env.example           # Environment template
├── README.md              # Documentation
├── data/                  # SQLite storage for sessions & history
└── app/
    ├── config.py          # LLM client & server configuration
    ├── schemas.py         # Pydantic schemas (Agent 1, 2, 3 + API)
    ├── agents/
    │   ├── content_analyst.py     # Agent 1 (Outline Generator)
    │   ├── article_writer.py      # Agent 2 (Drafting & Revision)
    │   └── editorial_reviewer.py  # Agent 3 (Quality Control Auditor)
    ├── utils/
    │   ├── transcript.py  # YouTube transcript extraction
    │   └── chunking.py    # 5-minute time-slice segmenting
    ├── storage/
    │   └── session_store.py       # SQLite persistence for sessions & versions
    ├── graph/
    │   ├── state.py       # LangGraph state schema
    │   └── workflow.py    # LangGraph StateGraph pipeline
    └── api/
        ├── routes.py      # REST endpoints & SSE streaming
        └── main.py        # FastAPI app factory & CORS
```

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Copy `.env.example` to `.env` and set your OpenAI or Azure OpenAI credentials:
```bash
cp .env.example .env
```

### 3. Launch the Backend
```bash
python run.py
```

* **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 📡 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status |
| `POST` | `/api/sessions/generate` | Run full pipeline through Agent 3 to await human review |
| `GET` | `/api/sessions` | List all generation sessions |
| `GET` | `/api/sessions/{id}` | Get session details, artifacts, and version history |
| `POST` | `/api/sessions/{id}/human-review` | Submit human decisions (accept/reject issues, direct edits) |
| `POST` | `/api/sessions/{id}/revise` | Trigger Agent 2 revision with accepted human feedback |
| `POST` | `/api/sessions/{id}/approve` | Issue final human approval certificate for publication |
| `GET` | `/api/sessions/{id}/stream` | Stream live LangGraph node progress via Server-Sent Events (SSE) |
