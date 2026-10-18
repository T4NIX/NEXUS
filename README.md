# Project NEXUS

<div align="center">

<h3>Intelligent Natural Language to SQL Pipeline with OS Process Scheduling & ACID Relational Integrity</h3>

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-8E75C2?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Tests Passing](https://img.shields.io/badge/Pytest-22%2F22%20Passed-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](#-testing--verification)
[![License](https://img.shields.io/badge/License-MIT-amber?style=for-the-badge)](#-license)

</div>

---

## 📌 Overview

**NEXUS** is an end-to-end platform integrating **Operating Systems (OS)**, **Database Management Systems (DBMS)**, and **Artificial Intelligence (AI)** into a unified query execution pipeline.

Rather than executing natural-language database queries synchronously, **NEXUS virtualizes query execution as simulated Operating System Computational Processes (PCBs)**. Every query is assigned a unique `PID`, arrival timestamp, estimated CPU burst time, memory footprint, priority level, and state transitions (`NEW` &rarr; `READY` &rarr; `RUNNING` &rarr; `WAITING` &rarr; `COMPLETED` / `FAILED`). Jobs are dispatched across an asynchronous multi-threaded worker cluster using configurable multi-policy scheduling algorithms (FCFS, SJF, Priority, Round Robin), governed by concurrency primitives (Mutexes and Semaphores), validated for AST safety, and executed against a normalized relational database with full ACID atomicity.

---

## 🌟 Architecture & Execution Lifecycle

```
[ Frontend Client / User Dashboard ]
          │ (1) Submit NL / SQL Query + Priority
          ▼
   [ FastAPI Gateway ]
          │ (2) Initialize Process Control Block (PCB) with PID, Priority, Arrival Time
          ▼
  [ OS Ready Queue ] ◄──(Re-queues on RR Quantum Expiry)──┐
          │                                                │
          │ (3) Multi-Policy Scheduler (FCFS / SJF / Priority / RR)
          ▼                                                │
[ Asynchronous Worker Cluster ]                            │
 (Worker-1, Worker-2, Worker-3)                            │
  ├── [Mutex Lock]: Mutual exclusion on PCB claiming       │
  ├── [RAG Tracker]: Resource Allocation Graph deadlock monitoring
  ├── [AI Translator]: Google Gemini API / Semantic Offline Fallback
  ├── [AST Validator]: sqlglot AST verification & injection defense
  ├── [Cost Estimator]: Computational complexity & CPU burst estimation
  └── [Semaphore Control]: Limits concurrent DB connection pool (Max 3)
          │                                                │
          │ (4) Dispatch Safe SQL                          │
          ▼                                                │
[ DBMS Relational Engine ]                                 │
 (University Database: 3NF Schema + vw_student_performance)│
          │                                                │
          │ (5) Fetch Rows / Commit DML Mutation           │
          ▼                                                │
[ Atomic ACID Finalizer ] ─────────────────────────────────┘
  ├── Saves result records to System DB (nexus_system.db)
  ├── Computes Turnaround Time (TAT) and Waiting Time (WT)
  ├── Logs Context Switches & Worker CPU/Memory Telemetry
  └── Broadcasts Live Gantt & Telemetry updates to UI
```

---

## 👥 Team of Four & Responsibility Breakdown

| Team Member | Domain & Ownership | Core Responsibilities |
|---|---|---|
| **Member 1** | **AI & Operating Systems (OS)**<br/>`app/ai/`, `app/os/` | • LLM translation engine with Gemini API & schema context injection (`translator.py`, `prompt_templates.py`)<br/>• Offline deterministic semantic NLP fallback translator<br/>• Process Control Block (PCB) state machine & lifecycle (`process.py`)<br/>• Multi-policy scheduler: FCFS, SJF, Priority, and Round Robin (`scheduler.py`)<br/>• Concurrency control with Mutex locks & Semaphores (`worker_cluster.py`)<br/>• Resource Allocation Graph (RAG) & cycle-based deadlock detection (`deadlock_detector.py`) |
| **Member 2** | **Database Management Systems (DBMS)**<br/>`app/dbms/`, `app/models/db_models.py` | • University 3NF relational schema design & synthetic seed generator (`seed_data.py`)<br/>• Dual-engine persistence layer (`nexus_university.db`, `nexus_system.db`) (`connection.py`)<br/>• Security context isolation via database views (`vw_student_performance`)<br/>• Dynamic database schema introspection (`PRAGMA table_info`, `foreign_key_list`)<br/>• Referential integrity maintenance with cascading deletions (`routes_system.py`)<br/>• Query complexity & CPU burst cost estimation model (`cost_estimator.py`) |
| **Member 3** | **Frontend Engineering & UI/UX**<br/>`frontend/` | • React 18 + Vite responsive glassmorphic dashboard architecture (`App.jsx`)<br/>• Interactive Natural Language Query Console with preset templates (`QueryConsole.jsx`)<br/>• Live OS execution Gantt Chart timeline visualizer (`GanttChart.jsx`)<br/>• Real-time Process Ready Queue & PCB inspector modal (`ProcessQueue.jsx`)<br/>• Worker cluster node monitor & RAG deadlock telemetry (`WorkerMonitor.jsx`)<br/>• Dynamic DB Schema Manager with tuple insert modal & inline deletion (`SchemaViewer.jsx`) |
| **Member 4** | **FastAPI Python Backend with Validation**<br/>`app/api/`, `app/main.py`, `app/models/schemas.py` | • FastAPI REST gateway architecture, routing, and CORS middleware (`main.py`)<br/>• AST SQL Safety Validator enforcing read/write rules & injection blocking via `sqlglot` (`query_validator.py`)<br/>• Pydantic v2 data validation schemas with constraint enforcement (`schemas.py`)<br/>• Asynchronous API routes for query submission, queue inspection, and scheduling config<br/>• Safe DML mutation endpoints: validated tuple insertion and cascading row deletion<br/>• Comprehensive Pytest integration test suite with 100% passing test coverage (`tests/`) |

---

## 🛠️ GitHub Branch & Commit Conventions

To maintain a clean and collaborative Git workflow, the project adheres to the following branching model:

- `main` — Production release branch
- `develop` — Active integration branch
- `feature/member-1-ai-os` — AI Prompting, Gemini LLM, PCB & OS Multi-Policy Scheduler
- `feature/member-2-dbms` — Relational 3NF Schema, DB Views, Connection Pooling, Seed Data
- `feature/member-3-frontend` — React 18 UI Dashboard, Live Gantt Chart, Queue & Schema Viewer
- `feature/member-4-fastapi-backend` — FastAPI Endpoints, AST Security Validator, Pydantic Schemas

**Conventional Commit Syntax:**
```bash
feat(os): implement Round Robin time slicing with quantum ticks
feat(dbms): add dynamic foreign key introspection for domain tables
feat(ai): integrate Gemini schema prompt templates with DDL context
feat(api): enforce AST safety validation using sqlglot
feat(ui): add inline tuple deletion with instant schema synchronization
```

---

## 🔬 Core Technical Implementations

### 1. ⚙️ Operating Systems (OS) Engine
- **Process Control Block (PCB) State Machine (`app/os/process.py`)**:
  - Encapsulates queries as discrete computational jobs with `job_id` (PID starting at 100), user identity, arrival time ($T_{arr}$), estimated burst ticks ($T_{burst}$), RAM footprint (MB), priority (1–10), and state lifecycle:
    $$\text{NEW} \longrightarrow \text{READY} \longrightarrow \text{RUNNING} \longrightarrow \text{WAITING} \longrightarrow \text{COMPLETED} \ / \ \text{FAILED}$$
- **Multi-Policy CPU Scheduler (`app/os/scheduler.py`)**:
  - **FCFS (First-Come, First-Served)**: Non-preemptive FIFO queue ordered strictly by arrival time.
  - **SJF (Shortest Job First)**: Greedy minimization of average waiting time using cost-estimated burst times.
  - **Priority Scheduling**: Dispatches highest-priority administrative or urgent analytical queries first.
  - **Round Robin (RR)**: Preemptive time-slicing with configurable quantum ticks (`quantum_ticks = 2`), context-switch tracking, and queue re-insertion.
- **Concurrency & Synchronization Primitives (`app/os/worker_cluster.py`)**:
  - **Mutex Lock (`threading.Lock()`)**: Guards process retrieval and status updates, eliminating race conditions and double-dispatching across worker threads.
  - **Counting Semaphore (`threading.Semaphore(3)`)**: Throttles concurrent worker connections to the relational database to prevent connection exhaustion.
  - **Worker Cluster**: 3 asynchronous daemon worker threads (`Worker-1`, `Worker-2`, `Worker-3`) with dynamic CPU and RAM telemetry.
- **Deadlock Detection & Resource Allocation Graph (`app/os/deadlock_detector.py`)**:
  - Directed graph $G = (V, E)$ tracking thread-resource dependencies (`CPU_Unit`, `DB_Connection_Pool`, `Memory_Blocks`).
  - Depth-First Search (DFS) cycle-detection algorithm run on every dispatch to detect potential deadlocks.
- **OS Telemetry & Live Gantt Chart (`app/api/routes_scheduler.py`, `frontend/src/components/GanttChart.jsx`)**:
  - Real-time mathematical metrics:
    - **Turnaround Time:** $TAT = T_{comp} - T_{arr}$
    - **Waiting Time:** $WT = TAT - (T_{burst} \times 0.05)$
    - **Context Switches:** Increments on each CPU preemption and switch.
  - Interactive Gantt chart rendering color-coded execution timelines across worker nodes.

---

### 2. 🗄️ Database Management Systems (DBMS) Engine
- **Dual-Engine Persistence Layer (`app/dbms/connection.py`)**:
  - **System Database (`nexus_system.db`)**: Stores system operational data (`nexus_users`, `nexus_queries`, `nexus_jobs`).
  - **University Domain Database (`nexus_university.db`)**: 3NF normalized academic schema.
- **3NF Relational Domain Schema (`app/models/db_models.py`)**:
  - `departments`: `dept_id` [PK], `dept_name` [UNIQUE], `building`, `budget`
  - `students`: `student_id` [PK], `name`, `email` [UNIQUE], `dept_id` [FK &rarr; `departments`], `admission_year`, `cgpa`
  - `courses`: `course_id` [PK], `course_code` [UNIQUE], `course_name`, `credits`, `dept_id` [FK &rarr; `departments`]
  - `enrolments`: `enrolment_id` [PK], `student_id` [FK &rarr; `students`], `course_id` [FK &rarr; `courses`], `semester`, `year`
  - `marks`: `mark_id` [PK], `enrolment_id` [FK &rarr; `enrolments`], `exam_type`, `marks_obtained`, `max_marks`
- **Security Context Isolation via Views (`app/dbms/seed_data.py`)**:
  - Implements `vw_student_performance` to expose joined student, course, and examination data to the AI translation engine while strictly isolating and concealing system tables (`nexus_*`).
- **AST Security Validator (`app/dbms/query_validator.py`)**:
  - Powered by `sqlglot` to parse Abstract Syntax Trees before execution.
  - Blocks SQL injection attacks, semicolon-chained multi-statements (`SELECT 1; DROP TABLE students;`), unauthorized DDL against system tables, and privileged administrative commands (`GRANT`, `REVOKE`, `SHUTDOWN`, `ATTACH`).
- **Query Cost Estimator (`app/dbms/cost_estimator.py`)**:
  - Statically analyzes table joins, `GROUP BY` aggregations, and subqueries to calculate estimated CPU burst ticks and RAM footprint.
- **Dynamic Schema Inspection & Real-Time Mutation (`app/api/routes_system.py`, `frontend/src/components/SchemaViewer.jsx`)**:
  - Dynamic table discovery via SQLite `PRAGMA table_info` and `PRAGMA foreign_key_list`.
  - Type-safe tuple insertion with constraint validation and autoincrement primary key support.
  - Inline row deletion with automated cascading cleanup (`marks` &rarr; `enrolments` &rarr; `courses` / `students`).
  - Real-time schema synchronization updating record counts instantly upon deletion or insertion.
  - One-click database reset restoring sample domain records.

---

### 3. 🤖 Artificial Intelligence (AI / NLP) Pipeline
- **Google Gemini API (`app/ai/translator.py`)**:
  - Zero-shot natural language to SQL translation using `gemini-2.0-flash` / `gemini-1.5-flash` with dynamic schema context injection and system instruction boundaries.
- **Deterministic Semantic Offline Engine (`app/ai/translator.py`)**:
  - Comprehensive regex and keyword translation layer for offline development and testing. Supports complex queries, analytical aggregations, conversational inserts, and row deletions without requiring an active API key.

---

## 💻 Tech Stack

| Domain | Technologies |
|---|---|
| **Backend Core** | Python 3.10+, FastAPI, Uvicorn, Pydantic v2 |
| **ORM & Database** | SQLAlchemy 2.0, SQLite (WAL Mode), sqlglot (AST Parsing) |
| **Operating System Simulation** | Python `threading` (Mutex Locks, Semaphores, Daemon Worker Threads), NetworkX RAG Cycle Detection |
| **AI / LLM** | Google Gemini Generative AI SDK, Custom Semantic NLP Engine |
| **Frontend Dashboard** | React 18, Vite, Lucide React Icons, Modern Glassmorphism Vanilla CSS |
| **Testing & Quality** | Pytest, AnyIO, Starlette TestClient |

---

## 📁 Repository Directory Structure

```
NEXUS/
├── nexus_docs/                         # Architectural documentation and PDF guides
│   ├── Project_NEXUS_OS_and_DBMS_Architecture.pdf  # Generated 3-Page Concepts Guide
│   └── generate_nexus_core_concepts_pdf.py         # ReportLab PDF Generator Script
│
└── nexus_project/                      # Core Application Source Code
    ├── app/
    │   ├── ai/                         # AI & NLP Translation Layer
    │   │   ├── prompt_templates.py     # DDL context builder & system prompts
    │   │   └── translator.py           # Gemini API + Semantic offline translation engine
    │   ├── api/                        # REST API Endpoints
    │   │   ├── routes_query.py         # Query submission & job status tracking
    │   │   ├── routes_scheduler.py     # OS scheduler metrics, Ready Queue, config
    │   │   └── routes_system.py        # Schema introspection, insert-row, delete-row, reset
    │   ├── dbms/                       # Database Management Engine
    │   │   ├── connection.py           # Dual-engine SQLite connection management
    │   │   ├── cost_estimator.py       # Query complexity & CPU burst cost calculator
    │   │   ├── query_validator.py      # AST SQL safety & injection validator (sqlglot)
    │   │   └── seed_data.py            # 3NF university schema & sample data seeder
    │   ├── models/                     # Data Models & Schemas
    │   │   ├── db_models.py            # SQLAlchemy ORM relational models
    │   │   └── schemas.py              # Pydantic v2 API request/response schemas
    │   ├── os/                         # Operating System Simulation
    │   │   ├── deadlock_detector.py    # Resource Allocation Graph (RAG) & cycle detection
    │   │   ├── process.py              # Process Control Block (PCB) state machine
    │   │   ├── scheduler.py            # Multi-policy scheduler (FCFS, SJF, Priority, RR)
    │   │   └── worker_cluster.py       # Multi-threaded worker pool with Mutex & Semaphores
    │   ├── config.py                   # Application settings & environment loader
    │   └── main.py                     # FastAPI server initialization & background workers
    │
    ├── frontend/                       # React 18 + Vite Web Application
    │   ├── src/
    │   │   ├── components/
    │   │   │   ├── GanttChart.jsx      # Live OS CPU execution timeline visualizer
    │   │   │   ├── Navbar.jsx          # Clean navigation bar with live telemetry ticker
    │   │   │   ├── ProcessQueue.jsx    # Real-time Ready Queue & PCB inspector modal
    │   │   │   ├── QueryConsole.jsx    # NL query console, algorithm switcher, presets
    │   │   │   ├── ResultsTable.jsx    # SQL query execution result grid
    │   │   │   ├── SchemaViewer.jsx    # DB schema viewer, tuple insert modal, delete actions
    │   │   │   └── WorkerMonitor.jsx   # Worker node CPU/RAM status & RAG deadlock monitor
    │   │   ├── App.jsx                 # Main application dashboard layout & sync polling
    │   │   ├── index.css               # Modern glassmorphic dark theme stylesheet
    │   │   └── main.jsx                # React root mount
    │   ├── index.html                  # HTML entry point
    │   ├── package.json                # Frontend package dependencies
    │   └── vite.config.js              # Vite server & backend API proxy configuration
    │
    ├── tests/                          # Automated Pytest Suite
    │   ├── test_ai_translator.py       # AI & semantic SQL translation tests
    │   ├── test_dbms_validator.py      # AST security validator & cost estimator tests
    │   ├── test_integration.py         # End-to-end pipeline & API integration tests
    │   └── test_os_scheduler.py        # Scheduling algorithms & deadlock RAG tests
    │
    ├── .env.example                    # Environment variable template
    ├── requirements.txt                # Python backend dependencies
    └── README.md                       # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm**

---

### 2. Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/NEXUS.git
   cd NEXUS/nexus_project
   ```

2. **Create and activate a virtual environment:**
   - **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables (Optional):**
   ```bash
   cp .env.example .env
   ```
   *(Optional: Add your `GEMINI_API_KEY` in `.env`. If omitted, NEXUS automatically falls back to its built-in offline semantic translation engine).*

5. **Start the FastAPI backend server:**
   ```bash
   python -m app.main
   ```
   The backend will start at **`http://localhost:8000`** with interactive Swagger docs at **`http://localhost:8000/docs`**.

---

### 3. Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node dependencies:**
   ```bash
   npm install
   ```

3. **Start the Vite development server:**
   ```bash
   npm run dev
   ```
   The interactive dashboard will open at **`http://localhost:3000`**.

---

## 🧪 Testing & Verification

The project includes an automated test suite verifying all modules:

```bash
# Run pytest from the nexus_project root directory
pytest -v
```

### Test Coverage Highlights:
- **`tests/test_ai_translator.py`**: Validates prompt construction, conversational queries, DML commands, and offline translation.
- **`tests/test_dbms_validator.py`**: Tests AST security enforcement, SQL injection blocking, system table isolation, and query cost estimation.
- **`tests/test_os_scheduler.py`**: Verifies PCB state creation, FCFS arrival ordering, SJF burst optimization, Priority preemption, Round Robin re-queuing, and RAG deadlock cycle detection.
- **`tests/test_integration.py`**: End-to-end integration testing query submission, worker thread execution, schema introspection, and direct database mutation endpoints.

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/query/submit` | Enqueues a new natural language query as an OS Process (PCB). |
| `GET` | `/api/v1/query/{job_id}` | Fetches real-time status and execution telemetry of a specific job. |
| `GET` | `/api/v1/query/all/history` | Retrieves complete process history and execution metrics. |
| `GET` | `/api/v1/scheduler/metrics` | Returns active algorithm, turnaround time, waiting time, and context switches. |
| `GET` | `/api/v1/scheduler/queue` | Returns the current state of the OS Ready Queue. |
| `POST` | `/api/v1/scheduler/config` | Dynamically switches active scheduling algorithm (`FCFS`, `SJF`, `PRIORITY`, `RR`). |
| `GET` | `/api/v1/system/resources` | Returns worker thread states (CPU/RAM usage) and RAG Deadlock status. |
| `GET` | `/api/v1/system/db-schema` | Dynamically returns domain tables, columns (PK/FK metadata), and views. |
| `POST` | `/api/v1/system/db/insert-row` | Inserts a new tuple into a domain table with constraint validation. |
| `POST` | `/api/v1/system/db/delete-row` | Deletes a record by primary key with automated cascading cleanup. |
| `POST` | `/api/v1/system/db/reset` | Resets the university database back to default sample records. |
| `GET` | `/health` | Server health check and active worker thread count. |

---

## 📜 Architectural Guide PDF

A detailed, publication-ready 3-page guide explaining the theoretical foundation and practical implementation of OS and DBMS concepts in NEXUS is located in:

- **Path:** [`nexus_docs/Project_NEXUS_OS_and_DBMS_Architecture.pdf`](../nexus_docs/Project_NEXUS_OS_and_DBMS_Architecture.pdf)
- **Generator Script:** [`nexus_docs/generate_nexus_core_concepts_pdf.py`](../nexus_docs/generate_nexus_core_concepts_pdf.py)

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.
