import threading
from typing import List, Optional
from app.os.process import ProcessControlBlock
from app.os.metrics import metrics_collector

class MultiPolicyScheduler:
    """
    OS Scheduler supporting FCFS, SJF, Priority, and Round Robin algorithms.
    Dispatches ready processes to worker threads.
    """

    def __init__(self, algorithm: str = "SJF", quantum_ticks: int = 2):
        self.algorithm: str = algorithm.upper()
        self.quantum_ticks: int = quantum_ticks
        self.ready_queue: List[ProcessControlBlock] = []
        self.all_processes: List[ProcessControlBlock] = []
        self.lock = threading.Lock()

    def set_algorithm(self, algo: str, quantum: Optional[int] = None):
        with self.lock:
            if algo in ["FCFS", "SJF", "PRIORITY", "RR"]:
                self.algorithm = algo
            if quantum and quantum >= 1:
                self.quantum_ticks = quantum
            self._reorder_queue()

    def add_process(self, pcb: ProcessControlBlock):
        with self.lock:
            pcb.status = "READY"
            self.ready_queue.append(pcb)
            self.all_processes.append(pcb)
            self._reorder_queue()

    def _reorder_queue(self):
        """Reorders ready queue according to active scheduling algorithm."""
        if self.algorithm == "FCFS":
            self.ready_queue.sort(key=lambda p: p.arrival_time)
        elif self.algorithm == "SJF":
            self.ready_queue.sort(key=lambda p: p.estimated_burst_time)
        elif self.algorithm == "PRIORITY":
            self.ready_queue.sort(key=lambda p: p.priority, reverse=True)
        elif self.algorithm == "RR":
            # In Round Robin, order is preserved as FIFO queue
            pass

    def get_next_process(self) -> Optional[ProcessControlBlock]:
        with self.lock:
            if not self.ready_queue:
                return None
            self._reorder_queue()
            pcb = self.ready_queue.pop(0)
            metrics_collector.record_context_switch()
            return pcb

    def re_queue_process(self, pcb: ProcessControlBlock):
        """Used in Round Robin when process exhausts time quantum but still has remaining burst time."""
        with self.lock:
            pcb.status = "READY"
            self.ready_queue.append(pcb)
            metrics_collector.record_context_switch()

    def get_all_processes() -> List[ProcessControlBlock]:
        return self.all_processes

# Global Scheduler Instance
os_scheduler = MultiPolicyScheduler()

