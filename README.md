# 🎙️ PodResearch 2.0

Full-stack YouTube Article Generator using **LangChain**, **LangGraph**, **FastAPI**, **React (Vite)**, and a **Human-in-the-Loop (HITL)** review workflow.

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
    │  - Grounding Audit & Unsupported Claim Detection
    │  - Timestamp Provenance Verification
    │  - Uncertainties Section Validation
    ▼
[Human-in-the-Loop Review Stage] ◄────► [Agent 2 Revision Loop]
    │  - Accept / Reject Individual Suggestions
    │  - Direct Markdown Editing & Outline Inspection
    │  - Version Comparison
    ▼
[Official Publication Approval Certificate]
```

---

## 📂 Project Structure

```text
podresearch-agent/
├── run.sh                     # Single-command launcher (Backend + Frontend)
├── README.md                  # Project overview & documentation
├── .env                       # Root environment configuration
├── backend/                   # FastAPI + LangGraph Multi-Agent Backend
│   ├── run.py                 # Backend launcher (uvicorn)
│   ├── requirements.txt       # Python dependencies
│   ├── pyproject.toml         # Packaging metadata
│   ├── .env.example           # Environment configuration template
│   ├── README.md              # Backend & API documentation
│   └── app/
│       ├── config.py          # LLM client & settings (with timeout safeguards)
│       ├── schemas.py         # Pydantic v2 schemas for Agents 1-3 & API
│       ├── agents/
│       │   ├── content_analyst.py     # Agent 1 (Outline Generator)
│       │   ├── article_writer.py      # Agent 2 (Writer & Revision Engine)
│       │   └── editorial_reviewer.py  # Agent 3 (Quality Control Auditor)
│       ├── utils/
│       │   ├── transcript.py  # YouTube transcript extraction
│       │   └── chunking.py    # 5-minute time-slice segmenter
│       ├── services/
│       │   ├── devto_service.py       # Dev.to REST API automated publisher
│       │   └── medium_service.py      # Medium REST API publisher
│       ├── storage/
│       │   └── session_store.py       # Thread-safe SQLite persistence
│       ├── graph/
│       │   ├── state.py       # LangGraph state schema
│       │   └── workflow.py    # LangGraph StateGraph pipeline
│       └── api/
│           ├── routes.py      # REST endpoints & SSE streaming
│           └── main.py        # FastAPI app factory with CORS
│
├── frontend/                  # Modern React + Vite UI
│   ├── package.json           # Dependencies (React, Lucide icons, Vite)
│   ├── vite.config.js         # Dev server with /api proxy to FastAPI & allowedHosts
│   ├── index.html             # HTML entry point
│   └── src/
│       ├── App.jsx            # Main app orchestrating generation & HITL review
│       ├── api.js             # Fetch client for all backend endpoints
│       ├── index.css          # Responsive dark/modern developer UI styling
│       ├── main.jsx           # React DOM root
│       └── components/
│           ├── Header.jsx             # Top bar with backend health indicator
│           ├── PipelineStepper.jsx    # 6-stage visual pipeline tracker
│           ├── InputForm.jsx          # YouTube URL & audience options
│           ├── ArticleEditor.jsx      # Markdown preview, direct editor & outline tab
│           ├── EditorialFeedback.jsx  # Agent 3 issue cards, accept/reject & revision controls
│           └── FinalApprovalView.jsx  # Publication-ready view with Dev.to/Medium automation
│
└── legacy_v1/                 # Archived v1 prototypes and tests
```

---

## 🚀 Quickstart

### One-Command Launch (Backend + Frontend)

From the project root directory, run:

```bash
./run.sh
```

This script will automatically:
1. Detect Python (virtual environment or system) and Node/npm
2. Initialize `backend/.env` with your credentials if missing
3. Start the FastAPI backend on **http://localhost:8000**
4. Start the React Vite frontend on **http://localhost:3000**
5. Gracefully terminate both processes when you press `Ctrl+C`

---

### Manual Launch

#### 1. Start the Backend (Port 8000)

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env    # Configure your OpenAI or Azure OpenAI credentials
python run.py
```

- API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### 2. Start the React Frontend (Port 3000)

In a separate terminal:

```bash
cd frontend
npm install            # (Already installed)
npm run dev
```

- Open [http://localhost:3000](http://localhost:3000) in your browser.
- Vite automatically proxies `/api/*` requests to the FastAPI backend running on `localhost:8000`.

---

## 💡 Human-in-the-Loop Features

1. **Autonomous 3-Agent Run**: Enter a YouTube URL and click **Start Autonomous Pipeline**.
2. **Review & Audit**:
   - **Agent 3 Quality Control**: Review issues categorized by severity (`high`, `medium`, `low`) and type (`unsupported_claim`, `technical_concern`, `missing_content`, `timestamp_errors`).
   - **Accept or Reject**: Accept suggestions to send them into Agent 2's revision pass, or reject suggestions you want kept as is.
   - **Direct Editing**: Switch to the **Edit Directly** tab to refine any paragraph manually and save.
   - **Agent 1 Outline**: View original outline, key takeaways, and timestamps.
3. **Trigger Revision**: Click **Request Revision** to let Agent 2 update the article using your decisions.
4. **Approve & Publish**: When satisfied, click **Approve & Publish** to certify the draft, view the final article, and download `.md`.
5. **Publish to Medium**: Click **Publish to Medium**, paste your Medium Integration Token (or set it in `backend/.env`), select status (`draft` or `public`), add tags, and post directly to your Medium blog via the Medium REST API.
