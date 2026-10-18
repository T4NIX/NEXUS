import pytest
from app.os.process import ProcessControlBlock
from app.os.scheduler import MultiPolicyScheduler
from app.os.deadlock_detector import ResourceAllocationGraph

def test_pcb_creation():
    pcb = ProcessControlBlock(nl_query="Show top 5 students by CGPA", priority=8)
    assert pcb.job_id >= 100
    assert pcb.status == "NEW"
    assert pcb.priority == 8

def test_fcfs_scheduling_order():
    scheduler = MultiPolicyScheduler(algorithm="FCFS")
    
    p1 = ProcessControlBlock("Query arrived first", priority=5)
    p1.arrival_time = 100.0
    
    p2 = ProcessControlBlock("Query arrived second", priority=9)
    p2.arrival_time = 105.0
    
    p3 = ProcessControlBlock("Query arrived third", priority=2)
    p3.arrival_time = 110.0

    scheduler.add_process(p1)
    scheduler.add_process(p2)
    scheduler.add_process(p3)

    first = scheduler.get_next_process()
    assert first.job_id == p1.job_id
    
    second = scheduler.get_next_process()
    assert second.job_id == p2.job_id

def test_priority_scheduling_order():
    scheduler = MultiPolicyScheduler(algorithm="PRIORITY")
    
    p1 = ProcessControlBlock("Low priority query", priority=2)
    p2 = ProcessControlBlock("High priority admin query", priority=9)
    
    scheduler.add_process(p1)
    scheduler.add_process(p2)
    
    first = scheduler.get_next_process()
    assert first.job_id == p2.job_id  # Priority 9 comes before 2

def test_round_robin_requeue():
    scheduler = MultiPolicyScheduler(algorithm="RR", quantum_ticks=2)
    p1 = ProcessControlBlock("Round robin job", priority=5)
    scheduler.add_process(p1)
    
    proc = scheduler.get_next_process()
    assert proc.job_id == p1.job_id
    
    # Requeue when quantum expires
    scheduler.re_queue_process(proc)
    requeued = scheduler.get_next_process()
    assert requeued.job_id == p1.job_id

def test_rag_deadlock_detection():
    rag = ResourceAllocationGraph()
    # Create cycle: W1 -> CPU -> W2 -> RAM -> W1
    rag.add_edge("Worker-1", "CPU")
    rag.add_edge("CPU", "Worker-2")
    rag.add_edge("Worker-2", "RAM")
    rag.add_edge("RAM", "Worker-1")

    has_deadlock, cycle = rag.detect_deadlock()
    assert has_deadlock is True
    assert len(cycle) > 0
