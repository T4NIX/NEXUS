import time
import threading
from typing import Optional, List, Dict, Any

_pid_counter = 100
_pid_lock = threading.Lock()
_pid_initialized = False

def get_next_pid() -> int:
    global _pid_counter, _pid_initialized
    with _pid_lock:
        if not _pid_initialized:
            try:
                from app.dbms.connection import SystemSessionLocal
                from app.models.db_models import JobRecord
                from sqlalchemy import func
                db = SystemSessionLocal()
                try:
                    max_id = db.query(func.max(JobRecord.job_id)).scalar()
                    if max_id and max_id >= _pid_counter:
                        _pid_counter = max_id
                finally:
                    db.close()
            except Exception:
                pass
            _pid_initialized = True
        _pid_counter += 1
        return _pid_counter

class ProcessControlBlock:
    """
    Process Control Block (PCB) representing a simulated OS process for an analytical query.
    """
    def __init__(self, nl_query: str, user_id: str = "user_1", priority: int = 5):
        self.job_id: int = get_next_pid()  # Process ID (PID)
        self.user_id: str = user_id
        self.nl_query: str = nl_query
        self.generated_sql: Optional[str] = None
        
        # OS Lifecycle State: NEW -> READY -> RUNNING -> WAITING -> COMPLETED / FAILED
        self.status: str = "NEW"
        self.priority: int = max(1, min(10, priority))  # 1=Lowest, 10=Highest
        
        # Timing & Scheduling Metadata
        self.arrival_time: float = round(time.time(), 3)
        self.estimated_burst_time: int = 5  # CPU ticks
        self.remaining_burst_time: int = 5  # Ticks remaining for RR/SJF
        self.memory_mb: int = 64
        
        self.start_time: Optional[float] = None
        self.completion_time: Optional[float] = None
        self.turnaround_time: Optional[float] = None
        self.waiting_time: Optional[float] = None
        self.worker_id: Optional[str] = None
        
        # DBMS Safety & Execution Data
        self.safety_valid: bool = False
        self.validation_error: Optional[str] = None
        self.execution_result: Optional[List[Dict[str, Any]]] = None
        self.error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "user_id": self.user_id,
            "nl_query": self.nl_query,
            "generated_sql": self.generated_sql,
            "status": self.status,
            "priority": self.priority,
            "arrival_time": self.arrival_time,
            "estimated_burst_time": self.estimated_burst_time,
            "remaining_burst_time": self.remaining_burst_time,
            "memory_mb": self.memory_mb,
            "start_time": self.start_time,
            "completion_time": self.completion_time,
            "turnaround_time": self.turnaround_time,
            "waiting_time": self.waiting_time,
            "worker_id": self.worker_id,
            "safety_valid": self.safety_valid,
            "validation_error": self.validation_error,
            "execution_result": self.execution_result,
            "error_message": self.error_message,
        }

