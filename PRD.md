# Product Requirement Document (PRD)
# The Lenny Growth Assistant

## 1. Product Purpose & Objectives

The **Lenny Growth Assistant** is an intelligent, conversational product management and growth advisor powered by grounded retrieval over **Lenny's Podcast & Newsletter** transcript repository. It helps product managers, founders, growth leaders, and evaluators query tactical frameworks, frameworks, and insights shared by world-class product leaders (e.g., Shreyas Doshi, Elena Verna, Casey Winters, Brian Balfour, Gibson Biddle, Marty Cagan).

### Key Objectives:
- **Grounded Conversational Intelligence**: Provide high-accuracy, cited answers based strictly on transcript data.
- **Explicit Out-of-Bounds Refusal**: Acknowledge when transcript knowledge does not contain the answer, avoiding hallucinated advice.
- **Multi-Model Flexibility**: Support local Ollama execution as well as cloud LLMs (Anthropic Claude, OpenAI), allowing evaluators to switch models dynamically via UI or environment variables without code modification.
- **Interactive Artifact Generation**: Transform grounded answers into actionable **Ship 30 for 30** style essays and standalone, responsive **HTML/CSS artifacts** (framework cards, cheat sheets, comparison tables).
- **Sandboxed Visualization**: Safely isolate generated HTML artifacts in an `<iframe>` viewer to prevent XSS and stylesheet pollution.
- **Production-Grade Infrastructure**: Containerized with Docker Compose, covered by automated test suites, and fully documented.

---

## 2. Target Audience & Core Use Cases

### Target Audience:
- Product Managers (PMs), Product Leaders, Growth Engineers, Founders.
- Evaluators assessing the architecture, safety, RAG quality, and extensibility of the system.

### Core Use Cases:
1. **Framework & Strategy Search**:
   * *Query*: "What is Gibson Biddle's DHM framework for product strategy?"
   * *Response*: Grounded explanation citing Gibson Biddle's episode, with breakdown of Delight, Hard-to-copy, and Margin-enhancing metrics.
2. **Growth & PLG Advice**:
   * *Query*: "How does Elena Verna recommend setting up Product-Led Growth loops?"
   * *Response*: Detailed citations from Elena Verna's transcript detailing acquisition, retention, and monetization loops.
3. **Out-of-Domain Safety Check**:
   * *Query*: "How do I fix a flat tire on a bicycle?"
   * *Response*: Explicit refusal: *"The Lenny Growth Assistant knowledge base is focused on product management and growth. It does not contain information on fixing bicycle tires."*
4. **Ship 30 for 30 Essay Generation**:
   * *Action*: Click "Convert to Ship 30 Essay" on any response.
   * *Output*: Format into Hook, 1-2-3 actionable points, TL;DR, and clear takeaway.
5. **Interactive UI Artifact Generation**:
   * *Action*: Click "Generate Framework Artifact".
   * *Output*: Standalone HTML card component rendered in the Artifact Viewer.

---

## 3. Detailed System Architecture & Data Flow

```
+─────────────────────────────────────────────────────────────────+
|                      React + Vite Frontend                      |
|  [ Chat Window | Expandable Citations | Sandboxed Artifact View ]|
+────────────────────────────────┬────────────────────────────────+
                                 │ HTTP REST API / JSON
                                 ▼
+─────────────────────────────────────────────────────────────────+
|                       FastAPI Backend                           |
|  - API Controller: /chat, /sessions, /config/model, /artifacts  |
|  - Middleware: CORS, Error Handling, Structured Logger          |
+──────────────┬─────────────────┬──────────────────┬─────────────+
               │                 │                  │
               ▼                 ▼                  ▼
+──────────────────────+ +───────────────+ +──────────────────────+
|    Agent Layer       | | Retrieval RAG | | LLM Provider Router  |
| - Tool Router        | | - Chunker     | | - Ollama (Local)     |
| - Essay Synthesizer  | | - Embedding/  | | - Anthropic Claude   |
| - Artifact Synthesizer| |   TF-IDF      | | - OpenAI           |
|                      | | - Grounding   | | - Mock Provider      |
+──────────────────────+ +───────────────+ +──────────────────────+
                                 │
                                 ▼
+─────────────────────────────────────────────────────────────────+
|                    PostgreSQL Database                          |
|  - Tables: sessions, messages, transcript_chunks, artifacts     |
+─────────────────────────────────────────────────────────────────+
```

---

## 4. Ingestion & RAG Pipeline Specification

1. **Source Data Structure**:
   * Raw transcripts stored in `data/transcripts/` in JSON/Markdown format.
   * Metadata: `episode_id`, `title`, `guest`, `date`, `topic_tags`, `transcript_text`.
2. **Chunking Strategy**:
   * Chunk size: 350-500 words with 50-word sliding overlap.
   * Each chunk retains metadata: `chunk_id`, `guest_name`, `episode_title`, `start_line`, `timestamp`.
3. **Indexing & Retrieval**:
   * Hybrid retrieval combining vector similarity (cosine score) and BM25 / TF-IDF keyword matching.
   * Scoring formula: $Score = 0.7 \times VectorSimilarity + 0.3 \times BM25Score$.
4. **Grounding & Refusal Engine**:
   * Minimum relevance threshold $T = 0.45$.
   * If max score $< T$, the RAG engine triggers a grounded refusal response:
     `"The knowledge base does not contain sufficient information from Lenny's Podcast to answer this question."`
5. **Citations**:
   * Every response includes structured citation metadata: Guest Name, Episode Title, Episode Number, Timestamp/Segment link.

---

## 5. Agent / LLM Orchestration Architecture

The system uses an autonomous Agent Orchestrator pattern where the LLM decides tool invocation based on user intent:

- **Tool 1: `search_transcripts`**
  - Inputs: `query: str`, `top_k: int`
  - Output: Ranked list of grounded transcript chunks with source citations.
- **Tool 2: `generate_ship30_essay`**
  - Inputs: `topic: str`, `grounded_context: str`
  - Output: Ship 30 for 30 essay structured with Hook, Core Points, and Summary.
- **Tool 3: `generate_ui_artifact`**
  - Inputs: `title: str`, `content_type: html|markdown`, `data: dict`
  - Output: Clean responsive HTML component with embedded CSS.

---

## 6. Model Switching & Fallback Mechanics

The backend features an abstract `LLMProvider` interface:

```python
class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = None) -> str: pass
    
    @abstractmethod
    def get_model_info(self) -> dict: pass
```

Supported Providers:
1. `OllamaProvider`: Local LLM via `http://localhost:11434` (e.g., `llama3.2`, `qwen2.5`, `finetunned_model`).
2. `AnthropicProvider`: Cloud LLM via `https://api.anthropic.com` (`claude-3-5-sonnet-20241022`).
3. `OpenAIProvider`: Cloud LLM via `https://api.openai.com` (`gpt-4o-mini`).
4. `MockLLMProvider`: Deterministic fallback for test suites and offline demo execution.

Runtime Model Switching:
- Changing the active model via `POST /api/v1/config/model` updates the backend router instantaneously without requiring process restarts.

---

## 7. Artifact Generation & Isolation Specification

### Artifact Types:
1. **Ship 30 for 30 Essay**: Markdown document following the viral essay format (Clear Hook, 3 Key Takeaways, TL;DR, Action Step).
2. **Interactive HTML/CSS Component**: Visual card, comparison matrix, or framework diagram styled with modern CSS.

### Security Isolation:
- HTML artifacts are rendered inside an `<iframe>` element.
- The `iframe` attributes are locked to `sandbox="allow-scripts"` (disallowing top-level navigation, same-origin storage access, form submission).
- Content is injected via `srcdoc` to prevent external resource loading vulnerabilities.

---

## 8. Data Models & Database Schemas

```sql
CREATE TABLE sessions (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user' | 'assistant' | 'system'
    content TEXT NOT NULL,
    citations JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transcript_chunks (
    id VARCHAR(36) PRIMARY KEY,
    episode_id VARCHAR(100) NOT NULL,
    episode_title VARCHAR(255) NOT NULL,
    guest_name VARCHAR(100) NOT NULL,
    segment_info VARCHAR(100),
    content TEXT NOT NULL,
    embedding VECTOR(384)
);

CREATE TABLE artifacts (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) REFERENCES sessions(id) ON DELETE CASCADE,
    message_id VARCHAR(36) REFERENCES messages(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    artifact_type VARCHAR(50) NOT NULL, -- 'markdown' | 'html' | 'essay'
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## 9. API Endpoint Specifications

### Health & Config
- `GET /health`: Returns system status and database connectivity.
- `GET /api/v1/config/model`: Returns active LLM provider, current model name, and list of available providers.
- `POST /api/v1/config/model`: Body `{"provider": "ollama|anthropic|openai|mock", "model": "string"}`. Dynamic model switch.

### Sessions & Chat
- `GET /api/v1/sessions`: List active conversation sessions.
- `POST /api/v1/sessions`: Create a new session.
- `DELETE /api/v1/sessions/{id}`: Delete a session.
- `GET /api/v1/sessions/{id}/messages`: Get session message history.
- `POST /api/v1/chat`: Body `{"session_id": "string", "prompt": "string"}`. Runs RAG + Agent pipeline, returns response, citations, and generated artifacts.

### Artifacts
- `GET /api/v1/artifacts/{id}`: Fetch artifact details by ID.
- `GET /api/v1/sessions/{session_id}/artifacts`: Fetch all artifacts generated in a session.
- `POST /api/v1/artifacts/generate`: Explicitly trigger artifact generation from a message context.

---

## 10. Non-Functional Requirements

- **Security**: Strict CORS headers, HTML iframe sandboxing, clean environment variable handling (no hardcoded API keys).
- **Latency**: Sub-3-second RAG search; stream responses where supported.
- **Maintainability**: Modular monolith structure; clean separation between controllers, RAG service, Agent orchestrator, and storage.
- **Testability**: Pytest suite covering endpoints, RAG scoring, model switching, and out-of-domain refusal.
