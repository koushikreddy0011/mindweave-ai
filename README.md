# MindWeave AI 🧠✨

[![MindWeave AI CI](https://github.com/koushikreddy0011/mindweave-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/koushikreddy0011/mindweave-ai/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16%20%2B%20pgvector-336791?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![Docker](https://img.shields.io/badge/Docker-Multi--stage-2496ED?logo=docker&logoColor=white)](https://www.docker.com)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-3.6%20Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade, AI-powered knowledge exploration platform that transforms complex topics and technical PDF documents into interactive, hierarchical mindmaps with on-demand educational explanations.

---

## 🌟 Key Capabilities

* **Topic-to-Mindmap Synthesis:** Generates deeply structured concept hierarchies using Google Gemini 3.6 Flash, validated via recursive Pydantic schemas.
* **Document Grounding Engine (RAG):** Upload technical PDFs; PyMuPDF extracts text in memory, generates overlapping semantic chunks, and stores 768-dimensional vector embeddings in PostgreSQL via `pgvector`.
* **Interactive Canvas:** High-performance graph canvas powered by `@xyflow/react` v12 with custom node taxonomy (Root, Branch, Leaf), horizontal Bézier curves, mini-map, and debounced coordinate persistence.
* **Contextual Knowledge Panel:** Progressively loads 6-section educational breakdowns (*Overview*, *Detailed Explanation*, *How It Works*, *Key Concepts*, *Examples*, *Applications*, *Related Topics*) with PostgreSQL JSONB caching.
* **Asynchronous Processing Pipeline:** Long-running AI generations return instant `202 Accepted` handshakes; FastAPI `BackgroundTasks` process the hierarchy while the frontend polls in real time.
* **Enterprise Security & Isolation:** Multi-tenant workspace partitioning, Argon2id password hashing, JWT bearer authentication, and unprivileged non-root container execution.
* **High-Fidelity Offline Fallback:** Graceful fallback resilience for both hierarchy generation and node explanations ensuring 100% platform availability even when external AI API quotas are depleted.

---

## 🏗️ Architecture

```
                                [ Web Browser / Client ]
                                           │
                                           ▼ (Port 80 / 443)
                         ┌───────────────────────────────────┐
                         │      Nginx Reverse Proxy & CDN    │
                         │     (Frontend Container :80)      │
                         └─────────────────┬─────────────────┘
                                           │
                 ┌─────────────────────────┴─────────────────────────┐
                 │                                                   │
                 ▼ (/index.html, static JS/CSS)                      ▼ (/api/v1/* upstream)
      ┌─────────────────────────┐                         ┌─────────────────────────┐
      │  React 18 SPA (Nginx)   │                         │    FastAPI (Uvicorn)    │
      │  Vite + TypeScript      │                         │    Python 3.11 Runtime  │
      │  @xyflow/react Canvas   │                         │  Async Workers & Alembic │
      └─────────────────────────┘                         └────────────┬────────────┘
                                                                       │
                                             ┌─────────────────────────┴─────────────────────────┐
                                             │                                                   │
                                             ▼ (asyncpg pool)                                    ▼ (Google GenAI SDK)
                                ┌─────────────────────────┐                         ┌─────────────────────────┐
                                │ PostgreSQL 16 Database  │                         │ Google Gemini 3.6 Flash │
                                │ - Relational Graphs     │                         │ - Hierarchy Decomposer  │
                                │ - pgvector (768-dim)    │                         │ - Deep Explanation LLM │
                                │ - JSONB Explanation Caching│                      │ - text-embedding-004    │
                                └─────────────────────────┘                         └─────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, TypeScript 5.6, Vite 5.4, Tailwind CSS, `@xyflow/react` (React Flow 12), Zustand, Lucide React |
| **Backend** | Python 3.11, FastAPI 0.115, Uvicorn, SQLAlchemy 2.0 (AsyncIO), Alembic, Pydantic v2 |
| **AI & RAG** | Google Gemini 3.6 Flash (`google-genai`), PyMuPDF (`fitz`), `pgvector` (Vector 768) |
| **Database** | PostgreSQL 16 with `pgvector` extension and `asyncpg` async driver |
| **Security** | Argon2id (`pwdlib`), JWT (`pyjwt`), CORS middleware, Non-root Docker execution (UID 10001) |
| **DevOps & CI/CD** | Multi-stage Docker, Docker Compose, Nginx, GitHub Actions (Automated CI with live `pgvector`) |

---

## 🏆 Completed Development Phases & Invariants

| Phase | Milestone Name | Key Invariants & Features Completed |
| :---: | :--- | :--- |
| **1** | **Foundational Architecture & Workspaces** | PostgreSQL database schema with UUID keys, multi-tenant workspace partitioning, and cascade relationships. |
| **2** | **Authentication & Security Pipeline** | Argon2id password hashing, JWT bearer tokens, user registration, login, and active user resolution dependencies. |
| **3** | **Gemini AI Generation & Tree Normalizer** | Recursive Pydantic taxonomy schemas, Gemini 3.6 Flash prompt templates, 2D tree layout coordinates, and persistence. |
| **4** | **Interactive React Flow Mindmap Canvas** | Custom React Flow node types (`RootNode`, `BranchNode`, `LeafNode`), collapsible branches, zoom/fit-view controls, and mini-map. |
| **5** | **Deep-Dive Node Explanation Engine** | Contextual 6-section educational synthesis, JSONB caching, Markdown export, and high-fidelity offline fallback. |
| **6** | **Canvas State & Visual Exports** | Drag-and-drop node coordinate persistence, PNG snapshot generation, structured JSON graph export, and markdown curricula. |
| **7** | **Containerization, RAG & CI/CD** | Multi-stage Dockerfiles, Nginx orchestration, `pgvector` RAG pipeline with PyMuPDF chunking, GitHub Actions CI, and production runbook. |

---

## 🚀 Quick Start Guide

### Option 1: Production Stack (Recommended via Docker Compose)

#### Prerequisites
- [Docker Engine](https://docs.docker.com/engine/install/) 24.0+ & [Docker Compose](https://docs.docker.com/compose/) v2.20+
- Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

#### 1. Clone the Repository
```bash
git clone https://github.com/koushikreddy0011/mindweave-ai.git
cd mindweave-ai
```

#### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and insert your GEMINI_API_KEY
```

#### 3. Build & Launch Containers
```bash
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

#### 4. Access the Platform
- **Web Application:** [http://localhost](http://localhost)
- **API Documentation (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Probe:** [http://localhost/api/v1/health/ready](http://localhost/api/v1/health/ready)

---

### Option 2: Local Development Setup

#### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Set your DATABASE_URL and GEMINI_API_KEY in backend/.env

# Run Alembic migrations
alembic upgrade head

# Start FastAPI dev server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Vite server running on http://localhost:5173
```

---

## 🧪 Testing & Verification

### 1. Automated Backend Smoke Suite (Pytest)
```bash
cd backend
pytest tests/ -v
```

### 2. Full-Stack End-to-End Verification Script (9/9 Steps)
Validates auth, workspace provisioning, topic generation, polling, node explanations, and PDF extraction:
```bash
python backend/scripts/test_full_stack_e2e.py
```

### 3. Frontend Type-Check & Production Build
```bash
cd frontend
npm run build
# Compiles strict TypeScript and outputs production bundle in dist/
```

---

## 📜 Production Operations & Maintenance

Detailed production runbooks covering automated nightly backups with `pgvector` preservation, Let's Encrypt SSL/TLS termination, zero-downtime rolling deployments, and disaster recovery checklists are available in:

👉 **[Production Operations & Deployment Runbook](docs/production-deployment.md)**

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
