# Project NEXUS — AI Natural Language to SQL with OS Process Scheduling

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-cyan)](https://react.dev/)
[![Gemini API](https://img.shields.io/badge/AI-Google%20Gemini-purple)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-amber)](#)

> **NEXUS** is an academic platform integrating **Operating Systems (OS)**, **Database Management Systems (DBMS)**, and **Artificial Intelligence (AI)** into a unified query processing pipeline.

---
## Architecture & Core Concept

Rather than executing natural-language database queries synchronously, **NEXUS** encapsulates every query into a simulated **OS Computational Process (PCB)** with unique `PID`, arrival time, estimated CPU burst time, RAM footprint, priority, and state transitions (`NEW` → `READY` → `RUNNING` → `WAITING` → `COMPLETED` / `FAILED`).

```
[ Frontend / User Input ]
       │  (1) Submit NL Question
       ▼
[ FastAPI Gateway ] ──(Enqueues PCB Job)──► [ OS Multi-Policy Scheduler ]
                                                 (FCFS / SJF / Priority / RR)
                                                              │
[ DBMS Execution Engine ] ◄──(Executes Safe SQL)── [ Worker Thread Cluster ]
  (University Relational DB)                              (AI Translate + AST Validate)
```

---
## 🔬 Domain Integrations

  \### 1. Operating Systems (OS) Engine
- **Process Control Block (PCB)**: Tracks PID, status, priority, burst ticks, turnaround time ($TAT = T_{comp} - T_{arr}$), waiting time ($WT = TAT - T_{burst}$), context switches.
- **Multi-Policy Scheduler**: Supports **FCFS**, **SJF (Shortest Job First)**, **Priority Scheduling**, and **Round Robin** (with configurable time quantum).
- **Concurrency Control**: Multi-threaded Worker Cluster (Worker-1, Worker-2, Worker-3) using **Mutex Locks** (prevent double claiming) and **Semaphores** (connection pool throttling).
- **Deadlock Detection**: Resource Allocation Graph (RAG) tracking thread-resource dependencies with cycle detection algorithms.

  ### 2. Artificial Intelligence (AI / NLP) Pipeline
- **Google Gemini API**: `gemini-2.5-flash` model with system instructions and DDL context injection.
- **Offline Fallback Engine**: Smart mock pattern translator ensuring 100% test reliability even without an API key.

- ### 3. Database Management Systems (DBMS) Engine
- **Relational Schema**: University Academic & Examination System (`departments`, `students`, `courses`, `enrolments`, `marks`).
- **Database Views**: Schema context isolation using `vw_student_performance` to expose domain data while hiding system metadata tables (`nexus_jobs`, `nexus_queries`, `nexus_users`).
- **AST Security Validator**: Parse & enforce read-only `SELECT` rules via `sqlglot`. Blocks `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`, and multi-statement injection.
- **ACID Transactions**: Atomic updating of job completion status + query result metadata in a single transaction.
