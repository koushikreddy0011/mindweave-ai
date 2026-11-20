# MindWeave AI — Product Requirements & UI/UX Specification

**Version:** 1.0  
**Status:** Initial Product Specification  
**Product Type:** AI-powered SaaS knowledge exploration platform

## 1. Product Vision

MindWeave AI transforms topics, documents and research materials into interactive hierarchical mindmaps with contextual explanations for every concept.

The goal is to combine visual knowledge organization, AI-powered explanations and document intelligence into a unified learning and research environment.

## 2. Target Audience

- Students and self-learners.
- Researchers and academics.
- Software developers and technology professionals.
- Business analysts and knowledge workers.

## 3. Core MVP Features

1. Topic-to-mindmap generation.
2. PDF-to-mindmap generation.
3. Interactive hierarchical graph visualization.
4. Detailed explanations for individual nodes.
5. Related concepts and contextual navigation.
6. Persistent mindmap storage.
7. Node editing and branch expansion.
8. PNG, PDF and Markdown exports.

## 4. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite + TypeScript |
| UI | Tailwind CSS + shadcn/ui |
| Visualization | React Flow |
| Backend | Python + FastAPI |
| AI Provider | Google Gemini |
| AI Orchestration | LangGraph |
| Validation | Pydantic |
| Database | PostgreSQL |
| Vector Search | pgvector |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Background Jobs | Redis + Celery |
| Document Processing | PyMuPDF |
| Deployment | Docker + AWS |
| CI/CD | GitHub Actions |

## 5. Application Routes

- `/` — Landing page
- `/dashboard` — User dashboard
- `/create` — Create mindmap
- `/mindmaps/:id` — Mindmap editor
- `/settings` — User preferences

## 6. UI Layout

### Dashboard
- Navigation sidebar.
- Search bar.
- Create new mindmap action.
- Recent mindmaps.
- Workspace management.

### Create Mindmap
- Topic input mode.
- Document upload mode.
- Generation depth settings.
- Explanation difficulty settings.
- Include examples option.
- Generate button.

### Mindmap Editor
- Left: Workspace and node navigation.
- Center: Interactive mindmap canvas.
- Right: Selected node's detailed explanation.

### Knowledge Panel
- Overview.
- Detailed explanation.
- How it works.
- Examples.
- Applications.
- Key takeaways.
- Related concepts.
- Source citations.

### Document Workspace
- PDF uploads.
- Processing status.
- Document metadata.
- Source management.

### Settings
- User profile.
- Default generation preferences.
- AI usage.
- Security settings.

## 7. Functional Requirements

| ID | Feature | Priority |
|---|---|---|
| FR-01 | User authentication | P0 |
| FR-02 | Topic-based generation | P0 |
| FR-03 | PDF-based generation | P0 |
| FR-04 | Structured hierarchy | P0 |
| FR-05 | Interactive graph | P0 |
| FR-06 | Node explanations | P0 |
| FR-07 | Save and retrieve mindmaps | P0 |
| FR-08 | Edit and expand nodes | P1 |
| FR-09 | Source-grounded explanations | P1 |
| FR-10 | URL ingestion | P1 |
| FR-11 | Quizzes and flashcards | P2 |
| FR-12 | Collaboration | P2 |

## 8. Main User Journey

1. User creates an account.
2. User opens the dashboard.
3. User creates a new mindmap.
4. User enters a topic or uploads a PDF.
5. AI generates a hierarchical knowledge graph.
6. Application validates and stores the graph.
7. Interactive mindmap appears.
8. Explanations are generated progressively.
9. User selects nodes to explore detailed knowledge.
10. User edits, saves or exports the mindmap.

## 9. Core Engineering Principles

- Structured LLM output validated using Pydantic.
- Hierarchy-first graph generation.
- Progressive node explanation generation.
- PostgreSQL as the source of truth.
- pgvector for document retrieval.
- Asynchronous processing for expensive operations.
- Source-grounded explanations for uploaded documents.
- Token tracking and generation cost monitoring.
- Authentication and resource-level authorization.

## 10. MVP Acceptance Criteria

The MVP is considered functional when:

- A user can register and log in.
- A user can create a mindmap from a topic.
- A user can upload a supported PDF.
- The AI can generate a valid hierarchical graph.
- Nodes can be visualized and selected.
- Selecting a node displays its explanation.
- Nodes and explanations persist in the database.
- Users can revisit their saved mindmaps.
- Invalid AI outputs and failed jobs are handled safely.

## 11. Out of Scope for Initial MVP

- Real-time multi-user collaboration.
- Subscription billing.
- Enterprise administration.
- Mobile applications.
- Autonomous multi-agent research.
- Advanced team analytics.

## 12. Initial Design Direction

**Visual style:** Minimal, professional, light-first SaaS interface.

**Primary colors:** Navy, blue and purple.

**Typography:** Inter or Geist Sans.

**Editor layout:** Three-panel workspace with left navigation, central graph canvas and right knowledge panel.

**Product positioning:** An interactive AI knowledge exploration platform, rather than a conventional mindmap generator.