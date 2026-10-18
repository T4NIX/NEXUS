import time
from typing import List, Dict, Any
from app.os.process import ProcessControlBlock

class OSMetricsCollector:
    """
    Calculates OS process scheduling performance metrics:
    - Average Turnaround Time (TAT)
    - Average Waiting Time (WT)
    - Total Context Switches
    - CPU Utilization %
    """

    def __init__(self):
        self.context_switches: int = 0
        self.total_processed_ticks: int = 0
        self.start_clock: float = time.time()

    def record_context_switch(self):
        self.context_switches += 1

    def calculate_metrics(self, all_processes: List[ProcessControlBlock], active_algo: str, quantum: int) -> Dict[str, Any]:
        total = len(all_processes)
        queued = sum(1 for p in all_processes if p.status in ["NEW", "READY"])
        running = sum(1 for p in all_processes if p.status in ["RUNNING", "RUNNING_AI", "RUNNING_DB"])
        completed_procs = [p for p in all_processes if p.status == "COMPLETED"]
        failed_procs = [p for p in all_processes if p.status == "FAILED"]
        
        comp_count = len(completed_procs)
        
        avg_tat = round(sum(p.turnaround_time for p in completed_procs if p.turnaround_time) / comp_count, 2) if comp_count > 0 else 0.0
        avg_wt = round(sum(p.waiting_time for p in completed_procs if p.waiting_time) / comp_count, 2) if comp_count > 0 else 0.0
        
        elapsed = max(1.0, time.time() - self.start_clock)
        cpu_util = round(min(100.0, (running * 35.0 + (comp_count * 10.0 / elapsed))), 1) if total > 0 else 0.0

        return {
            "active_algorithm": active_algo,
            "quantum_ticks": quantum,
            "total_jobs": total,
            "queued_jobs": queued,
            "running_jobs": running,
            "completed_jobs": comp_count,
            "failed_jobs": len(failed_procs),
            "avg_turnaround_time": avg_tat,
            "avg_waiting_time": avg_wt,
            "total_context_switches": self.context_switches,
            "cpu_utilization_pct": cpu_util
        }

metrics_collector = OSMetricsCollector()

