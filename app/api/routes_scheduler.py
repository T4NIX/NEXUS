from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import SchedulerConfigRequest, SchedulerMetricsResponse, ProcessControlBlockResponse
from app.os.scheduler import os_scheduler
from app.os.metrics import metrics_collector
from app.api.routes_query import pcb_store

router = APIRouter(prefix="/scheduler", tags=["OS Scheduler Controls"])

@router.get("/queue", response_model=List[ProcessControlBlockResponse])
def get_ready_queue():
    """Fetches processes currently waiting in the OS Ready Queue."""
    with os_scheduler.lock:
        return [ProcessControlBlockResponse(**p.to_dict()) for p in os_scheduler.ready_queue]

@router.post("/config", response_model=SchedulerMetricsResponse)
def update_scheduler_config(config: SchedulerConfigRequest):
    """
    Updates the active CPU scheduling algorithm (FCFS, PRIORITY, RR) and time quantum.
    Instantly re-sorts the Ready Queue.
    """
    algo = config.algorithm.upper()
    if algo not in ["FCFS", "PRIORITY", "RR"]:
        raise HTTPException(status_code=400, detail="Invalid algorithm. Supported: FCFS, PRIORITY, RR.")

    os_scheduler.set_algorithm(algo, config.quantum_ticks)
    
    all_procs = list(pcb_store.values())
    metrics = metrics_collector.calculate_metrics(all_procs, os_scheduler.algorithm, os_scheduler.quantum_ticks)
    return SchedulerMetricsResponse(**metrics)

@router.get("/metrics", response_model=SchedulerMetricsResponse)
def get_scheduler_metrics():
    """Fetches real-time OS scheduling telemetry (Turnaround Time, Waiting Time, Context Switches)."""
    all_procs = list(pcb_store.values())
    metrics = metrics_collector.calculate_metrics(all_procs, os_scheduler.algorithm, os_scheduler.quantum_ticks)
    return SchedulerMetricsResponse(**metrics)
