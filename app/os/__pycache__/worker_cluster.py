import time
import threading
import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.os.process import ProcessControlBlock
from app.os.scheduler import os_scheduler
from app.os.deadlock_detector import rag
from app.ai.translator import AITranslator
from app.dbms.query_validator import SQLQueryValidator
from app.dbms.cost_estimator import QueryCostEstimator
from app.dbms.connection import UniversitySessionLocal, SystemSessionLocal
from app.models.db_models import JobRecord, QueryRecord

# Synchronization Primitives (OS Concurrency Concepts)
worker_lock = threading.Lock()  # Mutex Lock to prevent race conditions on job claiming
db_semaphore = threading.Semaphore(3)  # Semaphore limiting maximum 3 concurrent DB connections

class WorkerNode:
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.status = "IDLE"  # IDLE, BUSY
        self.current_job: ProcessControlBlock = None
        self.cpu_usage_pct = 0.0
        self.memory_usage_mb = 0

class DistributedWorkerCluster:
    """
    Simulates a cluster of worker nodes (Worker-1, Worker-2, Worker-3)
    processing queued OS jobs asynchronously.
    """

    def __init__(self, num_workers: int = 3):
        self.workers: List[WorkerNode] = [WorkerNode(f"Worker-{i+1}") for i in range(num_workers)]
        self.is_running = False
        self.threads: List[threading.Thread] = []

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        for worker in self.workers:
            t = threading.Thread(target=self._worker_loop, args=(worker,), daemon=True)
            t.start()
            self.threads.append(t)

    def stop(self):
        self.is_running = False

    def _worker_loop(self, worker: WorkerNode):
        while self.is_running:
            # 1. Fetch next process from OS Scheduler
            pcb = os_scheduler.get_next_process()
            if not pcb:
                time.sleep(0.5)
                continue

            # Mutex acquisition: claim process
            with worker_lock:
                worker.status = "BUSY"
                worker.current_job = pcb
                pcb.status = "RUNNING"
                pcb.worker_id = worker.worker_id
                pcb.start_time = round(time.time(), 3)
                
                # Update Deadlock RAG graph
                rag.add_edge(worker.worker_id, "CPU_Unit")
                rag.add_edge("CPU_Unit", f"Memory_Block_{pcb.job_id}")

            try:
                # ----------------------------------------------------
                # Step 1: AI Translation (NL -> SQL)
                # ----------------------------------------------------
                generated_sql = AITranslator.translate(pcb.nl_query)
                pcb.generated_sql = generated_sql

                # Estimate Burst & Memory Cost
                burst_ticks, mem_mb = QueryCostEstimator.estimate_cost(generated_sql)
                pcb.estimated_burst_time = burst_ticks
                pcb.memory_mb = mem_mb
                worker.memory_usage_mb = mem_mb
                worker.cpu_usage_pct = round(burst_ticks * 12.5, 1)

                # ----------------------------------------------------
                # Step 2: SQL Safety AST Validation
                # ----------------------------------------------------
                is_safe, val_msg = SQLQueryValidator.validate_sql(generated_sql)
                pcb.safety_valid = is_safe
                pcb.validation_error = val_msg

                if not is_safe:
                    pcb.status = "FAILED"
                    pcb.error_message = f"Validation Error: {val_msg}"
                else:
                    # ----------------------------------------------------
                    # Step 3: DBMS Execution with Semaphore Control
                    # ----------------------------------------------------
                    with db_semaphore:
                        # Update RAG for DB connection
                        rag.add_edge(worker.worker_id, "DB_Connection_Pool")
                        
                        db: Session = UniversitySessionLocal()
                        try:
                            result_proxy = db.execute(text(generated_sql))
                            if result_proxy.returns_rows:
                                keys = result_proxy.keys()
                                rows = [dict(zip(keys, row)) for row in result_proxy.fetchall()]
                                pcb.execution_result = rows
                            else:
                                db.commit()
                                upper_sql = generated_sql.strip().upper()
                                action = "modified"
                                if upper_sql.startswith("INSERT"):
                                    action = "inserted"
                                elif upper_sql.startswith("DELETE"):
                                    action = "deleted"
                                elif upper_sql.startswith("UPDATE"):
                                    action = "updated"
                                pcb.execution_result = [{
                                    "affected_rows": result_proxy.rowcount,
                                    "operation": action.upper(),
                                    "message": f"Successfully {action} {result_proxy.rowcount} row(s)."
                                }]
                            pcb.status = "COMPLETED"
                        except Exception as db_ex:
                            db.rollback()
                            pcb.status = "FAILED"
                            pcb.error_message = f"Database Execution Error: {str(db_ex)}"
                        finally:
                            db.close()
                            rag.remove_edge(worker.worker_id, "DB_Connection_Pool")

            except Exception as ex:
                pcb.status = "FAILED"
                pcb.error_message = f"Process Failure: {str(ex)}"

            finally:
                # ----------------------------------------------------
                # Step 4: Finalize Metrics & Save to System Database
                # ----------------------------------------------------
                pcb.completion_time = round(time.time(), 3)
                pcb.turnaround_time = round(pcb.completion_time - pcb.arrival_time, 3)
                # Waiting time = Turnaround time - (simulated burst ticks * 0.05s)
                burst_secs = pcb.estimated_burst_time * 0.05
                pcb.waiting_time = max(0.0, round(pcb.turnaround_time - burst_secs, 3))

                # Save transaction in single atomic unit to System DB
                self._save_job_record(pcb)

                # Reset worker status & cleanup RAG graph
                with worker_lock:
                    worker.status = "IDLE"
                    worker.current_job = None
                    worker.cpu_usage_pct = 0.0
                    worker.memory_usage_mb = 0
                    rag.remove_edge(worker.worker_id, "CPU_Unit")
                    rag.remove_edge("CPU_Unit", f"Memory_Block_{pcb.job_id}")

    def _save_job_record(self, pcb: ProcessControlBlock):
        """Persists job completion metadata to nexus_jobs in single transaction."""
        sys_db: Session = SystemSessionLocal()
        try:
            # First create query record
            q_rec = QueryRecord(
                user_id=pcb.user_id,
                nl_text=pcb.nl_query,
                generated_sql=pcb.generated_sql
            )
            sys_db.add(q_rec)
            sys_db.flush()

            # Create Job record
            j_rec = JobRecord(
                job_id=pcb.job_id,
                query_id=q_rec.query_id,
                status=pcb.status,
                priority=pcb.priority,
                arrival_time=pcb.arrival_time,
                estimated_burst_time=pcb.estimated_burst_time,
                memory_mb=pcb.memory_mb,
                start_time=pcb.start_time,
                completion_time=pcb.completion_time,
                turnaround_time=pcb.turnaround_time,
                waiting_time=pcb.waiting_time,
                worker_id=pcb.worker_id,
                is_safe=pcb.safety_valid,
                error_log=pcb.error_message or pcb.validation_error,
                result_json=json.dumps(pcb.execution_result[:5]) if pcb.execution_result else None
            )
            sys_db.add(j_rec)
            sys_db.commit()
        except Exception as e:
            sys_db.rollback()
            print(f"Error saving job record: {e}")
        finally:
            sys_db.close()

# Global Worker Cluster
worker_cluster = DistributedWorkerCluster(num_workers=3)

