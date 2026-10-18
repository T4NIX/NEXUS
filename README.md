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
