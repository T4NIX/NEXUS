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
