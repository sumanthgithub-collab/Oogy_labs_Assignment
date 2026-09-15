# Implementation Plan: The Lenny Growth Assistant

## 1. Current Repository State
- **Workspace Path**: `c:\Users\suman\Downloads\OogyLabs`
- **Current State**: Initial clean directory.
- **Available Tooling**:
  - Python 3.14.4 installed (`py`)
  - Node.js & npm installed (`node`, `npm`)
  - Docker & Docker Compose available (`docker compose`)
  - Ollama installed & running (`http://localhost:11434`)

## 2. Proposed System Architecture

The Lenny Growth Assistant is designed as a modular monolith adhering to production-grade engineering principles:

```
┌─────────────────────────────────────────────────────────────┐
│                 React + TypeScript + Vite                   │
│        (Chat Interface, Artifact Viewer, Model Selector)    │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST / JSON
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Application Backend                 │
│ ┌───────────────┐ ┌────────────────┐ ┌────────────────────┐ │
│ │  API Routes   │ │  Agent Layer   │ │ Dynamic LLM Router │ │
│ └───────┬───────┘ └───────┬────────┘ └─────────┬──────────┘ │
└─────────┼─────────────────┼────────────────────┼────────────┘
          │                 │                    │
          ▼                 ▼                    ▼
┌──────────────────┐ ┌───────────────┐ ┌──────────────────────┐
│ Retrieval Engine │ │ PostgreSQL /  │ │ LLM Providers        │
│  (RAG & Hybrid   │ │ SQLite        │ │ - Ollama (Local)     │
│  Search)         │ │ (Metadata/    │ │ - Anthropic Claude   │
│                  │ │ Chunks/DB)    │ │ - OpenAI             │
│                  │ │               │ │ - Mock (Fallback)    │
└──────────────────┘ └───────────────┘ └──────────────────────┘
```

## 3. Implementation Phases

### Phase 1: Planning & Documentation (Completed)
- Inspect environment & verify local runtime capabilities.
- Draft `PRD.md` and `docs/implementation-plan.md`.
- Initialize project structure.

### Phase 2: Ingestion & RAG Retrieval Engine
- Build transcript ingestion pipeline (`scripts/ingest_transcripts.py`).
- Pre-populate authentic transcripts from Lenny's Podcast featuring top product/growth guests (Shreyas Doshi, Elena Verna, Casey Winters, Brian Balfour, Gibson Biddle, Marty Cagan).
- Implement chunking with metadata tracking (guest, episode title, timestamp, line number).
- Implement hybrid search & vector scoring with explicit out-of-domain refusal when context relevance is below threshold.

### Phase 3: Dynamic LLM Provider Abstraction & Agent Orchestration
- Implement `LLMProvider` base class and concrete implementations: `OllamaProvider`, `AnthropicProvider`, `OpenAIProvider`, `MockLLMProvider`.
- Build model configuration endpoint (`GET /api/v1/config/model`, `POST /api/v1/config/model`) enabling dynamic provider switching without app restart.
- Create Agent Orchestrator with tool selection:
  - `search_transcripts`
  - `generate_ship30_essay`
  - `generate_ui_artifact`

### Phase 4: Backend REST APIs & Persistence Layer
- Implement SQLAlchemy database models: `Session`, `Message`, `TranscriptChunk`, `Artifact`.
- Build FastAPI routes:
  - `/health`
  - `/api/v1/sessions` (CRUD, message history)
  - `/api/v1/chat` (Session-aware query processing with RAG & Agent tools)
  - `/api/v1/artifacts` (Fetch, filter, and render generated artifacts)
  - `/api/v1/config/model` (Dynamic model toggle)

### Phase 5: Frontend Interface & Sandboxed Artifact Viewer
- Build a responsive React + TypeScript frontend using Vite.
- Implement dark mode UI with amber/orange branding for Lenny's Growth Assistant.
- Sidebar with session history, new chat creation, and live model/provider selector widget.
- Chat message view with markdown rendering, expandable citation badges, and action buttons.
- Side Artifact Viewer supporting:
  - Markdown view
  - Raw HTML code view
  - Sandboxed `<iframe>` live preview (isolated via `sandbox="allow-scripts"` and `srcdoc`)
  - Ship 30 for 30 essay view

### Phase 6: Docker Compose Infrastructure & Packaging
- Create `Dockerfile.backend` and `Dockerfile.frontend`.
- Build `docker-compose.yml` orchestrating PostgreSQL, FastAPI backend, Vite frontend, and optional Ollama service profiles.

### Phase 7: Automated Testing & Verification
- Unit & Integration tests using `pytest`: API endpoints, RAG precision, provider switching, out-of-domain refusal.
- Frontend build verification via `npm run build`.
- Maintain engineering log in `docs/engineering-log.md`.

## 4. Assumptions & Design Decisions
1. **Lenny's Transcript Data**: Standardized transcript JSON/Markdown format containing speaker tags, transcript text, episode metadata, and guest info.
2. **Model Switching**: The app defaults to Ollama local (`finetunned_model` or configured model), switching seamlessly to Anthropic/OpenAI if API keys are provided, or falling back to a deterministic Mock provider if Ollama is unreachable.
3. **HTML Isolation**: LLM-generated HTML visual artifacts are rendered inside an isolated `<iframe>` using HTML5 `srcdoc` and strict sandbox attributes to protect against XSS and global CSS leakage.

## 5. Risk Assessment & Mitigation
- **Risk**: Ollama model latency or missing local model.
  - *Mitigation*: Graceful fallback to Mock LLM provider with clear UI notification.
- **Risk**: PostgreSQL service unavailable in local-only non-Docker environment.
  - *Mitigation*: Dual database driver support (PostgreSQL via asyncpg/psycopg2 and SQLite fallback).
- **Risk**: Grounding hallucination on out-of-domain queries.
  - *Mitigation*: Strict context relevance thresholding; explicit refusal prompt template.

## 6. Testing Strategy
- `backend/tests/test_api.py`: Test all HTTP endpoints.
- `backend/tests/test_rag.py`: Test chunking, vector search, citations, and out-of-bounds queries.
- `backend/tests/test_providers.py`: Verify provider switching mechanics.
- `frontend`: Static type checking & Vite production build check.
