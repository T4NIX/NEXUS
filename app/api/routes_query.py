from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.models.schemas import QuerySubmitRequest, QuerySubmitResponse, ProcessControlBlockResponse
from app.os.process import ProcessControlBlock
from app.os.scheduler import os_scheduler
from app.dbms.cost_estimator import QueryCostEstimator

router = APIRouter(prefix="/query", tags=["Query Operations"])

# Local cache of submitted process control blocks for instant REST lookup
pcb_store: Dict[int, ProcessControlBlock] = {}

@router.post("/submit", response_model=QuerySubmitResponse)
def submit_query(req: QuerySubmitRequest):
    """
    Submits a Natural Language query.
    1. Creates Process Control Block (PID)
    2. Enqueues job into OS Ready Queue (State: NEW -> READY)
    """
    if not req.nl_query or not req.nl_query.strip():
        raise HTTPException(status_code=400, detail="Natural Language query cannot be empty.")

    # Create Process Control Block
    pcb = ProcessControlBlock(
        nl_query=req.nl_query.strip(),
        user_id=req.user_id,
        priority=req.priority
    )
    
    # Store in memory cache
    pcb_store[pcb.job_id] = pcb
    
    # Enqueue into OS Ready Queue
    os_scheduler.add_process(pcb)
    
    return QuerySubmitResponse(
        job_id=pcb.job_id,
        nl_query=pcb.nl_query,
        status=pcb.status,
        priority=pcb.priority,
        estimated_burst_time=pcb.estimated_burst_time,
        arrival_time=pcb.arrival_time,
        message=f"Query converted to Job PID #{pcb.job_id} and added to OS Ready Queue under algorithm '{os_scheduler.algorithm}'."
    )

@router.get("/{job_id}", response_model=ProcessControlBlockResponse)
def get_query_status(job_id: int):
    """Fetches full Process Control Block (PCB) status for a given PID."""
    if job_id not in pcb_store:
        raise HTTPException(status_code=404, detail=f"Job PID #{job_id} not found.")
    
    pcb = pcb_store[job_id]
    return ProcessControlBlockResponse(**pcb.to_dict())

@router.get("/all/history", response_model=List[ProcessControlBlockResponse])
def get_all_query_history():
    """Returns history of all submitted jobs and their PCB details."""
    return [ProcessControlBlockResponse(**p.to_dict()) for p in pcb_store.values()]
