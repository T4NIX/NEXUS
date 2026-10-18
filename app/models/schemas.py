from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class QuerySubmitRequest(BaseModel):
    nl_query: str = Field(..., examples=["Show top 5 students by CGPA"])
    priority: int = Field(default=5, ge=1, le=10, description="Priority level (1=lowest, 10=highest)")
    user_id: str = Field(default="user_1")

class QuerySubmitResponse(BaseModel):
    job_id: int
    nl_query: str
    status: str
    priority: int
    estimated_burst_time: int
    arrival_time: float
    message: str

class ProcessControlBlockResponse(BaseModel):
    job_id: int
    user_id: str
    nl_query: str
    generated_sql: Optional[str] = None
    status: str
    priority: int
    arrival_time: float
    estimated_burst_time: int
    remaining_burst_time: int
    memory_mb: int
    start_time: Optional[float] = None
    completion_time: Optional[float] = None
    turnaround_time: Optional[float] = None
    waiting_time: Optional[float] = None
    worker_id: Optional[str] = None
    safety_valid: bool = False
    validation_error: Optional[str] = None
    execution_result: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None

class SchedulerConfigRequest(BaseModel):
    algorithm: str = Field(..., description="FCFS, PRIORITY, RR")
    quantum_ticks: Optional[int] = Field(default=2, ge=1, le=10)

class SchedulerMetricsResponse(BaseModel):
    active_algorithm: str
    quantum_ticks: int
    total_jobs: int
    queued_jobs: int
    running_jobs: int
    completed_jobs: int
    failed_jobs: int
    avg_turnaround_time: float
    avg_waiting_time: float
    total_context_switches: int
    cpu_utilization_pct: float

class WorkerStatus(BaseModel):
    worker_id: str
    status: str  # IDLE, BUSY
    current_job_id: Optional[int] = None
    cpu_usage_pct: float
    memory_usage_mb: int

class SystemResourcesResponse(BaseModel):
    workers: List[WorkerStatus]
    total_memory_mb: int
    used_memory_mb: int
    deadlock_detected: bool
    resource_allocation_graph: Dict[str, List[str]]
    active_connections: int
    max_connections: int

class TableSchemaDetail(BaseModel):
    table_name: str
    columns: List[Dict[str, str]]
    sample_rows: List[Dict[str, Any]]

class DatabaseSchemaResponse(BaseModel):
    tables: List[TableSchemaDetail]
    views: List[str]

class DeleteRowRequest(BaseModel):
    table_name: str
    primary_key: str
    key_value: Any

class DeleteColumnRequest(BaseModel):
    table_name: str
    column_name: str

class InsertStudentRequest(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Anubhav Joshi"})
    email: str = Field(..., json_schema_extra={"example": "anubhav.joshi@example.com"})
    dept_id: int = Field(..., description="Existing department ID")
    admission_year: int = Field(..., ge=1900, le=2100)
    cgpa: float = Field(..., ge=0.0, le=10.0)

class InsertRowRequest(BaseModel):
    table_name: str
    row_data: Dict[str, Any]

class DropTableRequest(BaseModel):
    table_name: str

class DbOperationResponse(BaseModel):
    status: str
    message: str
    affected_rows: Optional[int] = 0
