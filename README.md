# CampusAI — AI-Based College Academic Assistant

A full-stack, production-style AI academic assistant that helps college students navigate syllabi, academic regulations, exam guidelines, internship policies, and more — powered by RAG (Retrieval-Augmented Generation), LangGraph workflows, and a polished Next.js dashboard.

---

## Architecture

```
campus-ai/
├── backend/                 Python FastAPI backend
│   ├── app/
│   │   ├── api/             FastAPI route handlers (chat, documents, study plans, evaluation, dashboard)
│   │   ├── core/            Config (pydantic-settings) + logging
│   │   ├── database/        SQLAlchemy 2.0 models + async session management (SQLite)
│   │   ├── graph/           LangGraph state machine (6 nodes + study plan subgraph)
│   │   ├── prompts/         All LLM prompt strings (academic_qa, study_plan)
│   │   ├── rag/             RAG pipeline: document processor, embeddings, ChromaDB, retriever, LLM factory
│   │   ├── schemas/         Pydantic v2 request/response schemas
│   │   ├── services/        Business logic (chat, documents, study plans, evaluation, dashboard)
│   │   └── tools/           LangChain tools (calculator for study-hour math)
│   ├── data/
│   │   ├── sample_documents/  6 demo academic documents (syllabus, exam rules, internship, attendance, FAQ, regulations)
│   │   └── evaluation_dataset.json  10 benchmark test questions
│   ├── main.py              FastAPI entry point
│   ├── requirements.txt
│   └── .env.example
├── frontend/                Next.js 14 + TypeScript + Tailwind CSS
│   └── src/
│       ├── app/             App Router pages (dashboard, assistant, knowledge-base, study-planner, history, evaluation, settings)
│       ├── components/      Reusable UI components (no shadcn CLI required)
│       ├── hooks/           useChat, useDocuments, useStudyPlan
│       ├── lib/             API client, utils, constants
│       └── types/           TypeScript interfaces
└── README.md
```

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Recharts, Lucide React |
| Backend | Python 3.10+, FastAPI, SQLAlchemy 2.0 (SQLite), Pydantic v2 |
| AI/LLM | LangChain, LangGraph, OpenRouter |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) — runs locally, no API key |
| Vector DB | ChromaDB (persistent local storage) |
| RAG | Custom retrieval pipeline with source citations |

---

## Quick Setup

### 1. Backend

```powershell
cd campus-ai\backend

# Copy environment file
Copy-Item .env.example .env

# Edit .env and add your OpenRouter API key:
# OPENROUTER_API_KEY=your_key_here

# Install dependencies (Python 3.10+ required)
python -m pip install -r requirements.txt

# Start backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at: http://localhost:8000
API docs: http://localhost:8000/docs

### 2. Frontend

```powershell
cd campus-ai\frontend

# Install dependencies (Node.js 18+ required)
npm install

# Start frontend
npm run dev
```

Frontend runs at: http://localhost:3000

### 3. Load Sample Documents

After starting both servers:
1. Open http://localhost:3000
2. Go to **Knowledge Base**
3. Upload the files from `backend/data/sample_documents/`
4. Wait for status to show "Indexed"
5. Go to **AI Assistant** → select "Academic RAG" mode → ask questions!

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | — | **Required** OpenRouter API key |
| `LLM_PROVIDER` | `openrouter` | LLM provider |
| `OPENROUTER_MODEL` | `openai/gpt-4o-mini` | Default OpenRouter model |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace model for embeddings |
| `DATABASE_URL` | `sqlite+aiosqlite:///./campus_ai.db` | SQLite DB path |
| `CHROMADB_PATH` | `./data/chroma_db` | ChromaDB storage path |
| `RAG_CHUNK_SIZE` | `800` | Token chunk size for document splitting |
| `RAG_CHUNK_OVERLAP` | `150` | Chunk overlap tokens |
| `RAG_TOP_K` | `5` | Number of documents to retrieve |
| `RAG_SIMILARITY_THRESHOLD` | `0.3` | Minimum relevance score |
| `CONVERSATION_HISTORY_WINDOW` | `10` | Messages to include in history |
| `MAX_FILE_SIZE_MB` | `50` | Max upload size |
| `FRONTEND_URL` | `http://localhost:3000` | Allowed CORS origin |
| `DEMO_MODE` | `false` | Use mock responses (no API key needed) |

---

## Features

### AI Assistant
- **Two modes**: Basic LLM (general knowledge) vs Academic RAG (retrieval from college documents)
- **Conversational memory**: Follow-up questions maintain context
- **Source citations**: Every RAG answer cites the source document and excerpt
- **Markdown rendering**: Formatted responses with code blocks, tables, lists

### Knowledge Base
- Upload PDF, DOCX, and TXT files
- Automatic processing: text extraction → chunking → embedding → ChromaDB indexing
- Semantic search across indexed documents
- Document management: view status, delete with cascade vector cleanup

### Study Planner
- Wizard-based plan creation: subjects, exam dates, daily hours, priorities
- AI-generated daily schedule with study, revision, practice, and mock test sessions
- Natural language modifications: "Move DBMS session to Saturday", "I only have 2 hours now"
- Session completion tracking and CSV export

### RAG Evaluation
- Side-by-side comparison: Basic LLM vs Academic RAG
- 10 benchmark questions across 6 categories
- Metrics: response latency, groundedness score, citation presence
- Recharts visualizations

### LangGraph Workflow
```
analyze_query
    ├── (needs retrieval) → retrieve_information → generate_response
    └── (no retrieval)    → generate_response
                                    ↓
                             review_response
                                    ↓
                             finalize_response → END
```

---

## Sample Questions to Try

After uploading sample documents:
- "What is the minimum CGPA required for industry internship?" → from internship_guidelines.txt
- "How is CGPA calculated?" → from academic_regulations.txt
- "What happens if my attendance falls below 65%?" → from attendance_policy.txt
- "What are the passing marks for theory exams?" → from examination_guidelines.txt
- "What is the library borrowing limit?" → from student_handbook_faq.txt
- "What is the MBA program fee?" → Tests unknown-answer handling

---

## Important Notes

- **Demo documents**: The 6 sample documents in `data/sample_documents/` are fictional and labeled `[SAMPLE DOCUMENT - FOR DEMONSTRATION PURPOSES ONLY]`. They are not actual college policies.
- **Groundedness scores**: AI-estimated, not human-verified. Always review important academic information through official channels.
- **No authentication**: Session isolation uses a browser-generated UUID stored in localStorage.

---

## API Documentation

Interactive Swagger UI: http://localhost:8000/docs

Key endpoints:
- `POST /api/chat` — Send a message (Basic LLM or Academic RAG)
- `POST /api/documents/upload` — Upload and index a document
- `GET /api/documents` — List all documents
- `POST /api/study-plans/generate` — Generate a study plan
- `POST /api/study-plans/{id}/modify` — Modify plan via natural language
- `POST /api/evaluation/run` — Run LLM vs RAG comparison
- `GET /api/dashboard/stats` — Dashboard statistics
