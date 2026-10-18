from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from sqlalchemy import text
from app.models.schemas import (
    SystemResourcesResponse, WorkerStatus, DatabaseSchemaResponse, TableSchemaDetail,
    DeleteRowRequest, DeleteColumnRequest, DropTableRequest, DbOperationResponse, InsertRowRequest
)
from app.os.worker_cluster import worker_cluster
from app.os.deadlock_detector import rag
from app.dbms.connection import university_engine, UniversitySessionLocal
from app.dbms.seed_data import seed_university_data, reset_university_data

router = APIRouter(prefix="/system", tags=["System & DBMS Resources"])

@router.get("/resources", response_model=SystemResourcesResponse)
def get_system_resources():
    """Returns worker node states, CPU/Memory loads, and Deadlock RAG Graph status."""
    worker_statuses = []
    total_mem = 1536  # 3 Workers x 512MB
    used_mem = 0
    
    for w in worker_cluster.workers:
        used_mem += w.memory_usage_mb
        worker_statuses.append(WorkerStatus(
            worker_id=w.worker_id,
            status=w.status,
            current_job_id=w.current_job.job_id if w.current_job else None,
            cpu_usage_pct=w.cpu_usage_pct,
            memory_usage_mb=w.memory_usage_mb
        ))
        
    has_deadlock, cycle = rag.detect_deadlock()
    
    return SystemResourcesResponse(
        workers=worker_statuses,
        total_memory_mb=total_mem,
        used_memory_mb=used_mem,
        deadlock_detected=has_deadlock,
        resource_allocation_graph=rag.edges,
        active_connections=sum(1 for w in worker_cluster.workers if w.status == "BUSY"),
        max_connections=3
    )

@router.get("/db-schema", response_model=DatabaseSchemaResponse)
def get_database_schema():
    """Dynamically fetches University Database schema tables, columns, sample rows, and created views."""
    seed_university_data()

    table_details: List[TableSchemaDetail] = []
    views_list: List[str] = []
    db = UniversitySessionLocal()
    
    try:
        # Dynamically discover existing tables in SQLite (exclude internal sqlite and system tables)
        tbl_res = db.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'nexus_%' ORDER BY name;"
        )).fetchall()
        tables_list = [r[0] for r in tbl_res]
        
        # Dynamically discover views
        vw_res = db.execute(text(
            "SELECT name FROM sqlite_master WHERE type='view' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
        )).fetchall()
        views_list = [r[0] for r in vw_res]

        for tbl in tables_list:
            res = db.execute(text(f"PRAGMA table_info('{tbl}')")).fetchall()
            columns = [{"name": r[1], "type": r[2]} for r in res]
            
            sample_rows_res = db.execute(text(f"SELECT * FROM '{tbl}' LIMIT 50")).fetchall()
            col_names = [r[1] for r in res]
            sample_rows = [dict(zip(col_names, row)) for row in sample_rows_res]
            
            table_details.append(TableSchemaDetail(
                table_name=tbl,
                columns=columns,
                sample_rows=sample_rows
            ))
    finally:
        db.close()
        
    return DatabaseSchemaResponse(tables=table_details, views=views_list)

@router.post("/db/insert-row", response_model=DbOperationResponse)
def insert_database_row(req: InsertRowRequest):
    """Inserts a new tuple/row into a domain table."""
    clean_table = req.table_name.strip()
    if clean_table.lower().startswith("nexus_"):
        raise HTTPException(status_code=403, detail="Modification of internal system tables is restricted.")

    if not req.row_data:
        raise HTTPException(status_code=400, detail="Row data cannot be empty.")

    db = UniversitySessionLocal()
    try:
        chk = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name = :t"), {"t": clean_table}).fetchone()
        if not chk:
            raise HTTPException(status_code=404, detail=f"Table '{clean_table}' not found in database.")

        table_info = db.execute(text(f"PRAGMA table_info('{clean_table}')")).fetchall()
        valid_cols = {r[1]: r[2] for r in table_info}

        insert_cols = []
        insert_vals = {}
        for col_name, val in req.row_data.items():
            if col_name in valid_cols and val is not None and val != "":
                col_type = valid_cols[col_name].upper()
                try:
                    if "INT" in col_type:
                        val = int(val)
                    elif "FLOAT" in col_type or "REAL" in col_type or "NUMERIC" in col_type:
                        val = float(val)
                    else:
                        val = str(val).strip()
                except (ValueError, TypeError):
                    pass
                insert_cols.append(col_name)
                insert_vals[col_name] = val

        if not insert_cols:
            raise HTTPException(status_code=400, detail=f"No valid column data provided for table '{clean_table}'. Valid columns: {list(valid_cols.keys())}")

        cols_str = ", ".join([f'"{c}"' for c in insert_cols])
        params_str = ", ".join([f":{c}" for c in insert_cols])
        stmt = text(f'INSERT INTO "{clean_table}" ({cols_str}) VALUES ({params_str})')

        result = db.execute(stmt, insert_vals)
        db.commit()
        affected = result.rowcount if result.rowcount is not None and result.rowcount >= 0 else 1

        return DbOperationResponse(
            status="Success",
            message=f"Tuple inserted successfully into table '{clean_table}'.",
            affected_rows=affected
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database Insertion Error: {str(e)}")
    finally:
        db.close()

@router.post("/db/delete-row", response_model=DbOperationResponse)
def delete_database_row(req: DeleteRowRequest):
    """Deletes a single row from a domain table by primary key."""
    if req.table_name.lower().startswith("nexus_"):
        raise HTTPException(status_code=403, detail="Modification of internal system tables is restricted.")
        
    db = UniversitySessionLocal()
    try:
        stmt = text(f'DELETE FROM "{req.table_name}" WHERE "{req.primary_key}" = :val')
        result = db.execute(stmt, {"val": req.key_value})
        db.commit()
        affected = result.rowcount if result.rowcount is not None else 0
        return DbOperationResponse(
            status="Success",
            message=f"Deleted {affected} row(s) from table '{req.table_name}'.",
            affected_rows=affected
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to delete row: {str(e)}")
    finally:
        db.close()

@router.post("/db/delete-column", response_model=DbOperationResponse)
def delete_database_column(req: DeleteColumnRequest):
    """Drops a column from a domain table."""
    if req.table_name.lower().startswith("nexus_"):
        raise HTTPException(status_code=403, detail="Modification of internal system tables is restricted.")
        
    db = UniversitySessionLocal()
    try:
        stmt = text(f'ALTER TABLE "{req.table_name}" DROP COLUMN "{req.column_name}"')
        db.execute(stmt)
        db.commit()
        return DbOperationResponse(
            status="Success",
            message=f"Column '{req.column_name}' dropped from table '{req.table_name}'.",
            affected_rows=0
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to drop column: {str(e)}")
    finally:
        db.close()

@router.post("/db/drop-table", response_model=DbOperationResponse)
def drop_database_table(req: DropTableRequest):
    """Drops a domain table completely from the database."""
    if req.table_name.lower().startswith("nexus_"):
        raise HTTPException(status_code=403, detail="Dropping internal system tables is strictly restricted.")
        
    db = UniversitySessionLocal()
    try:
        stmt = text(f'DROP TABLE IF EXISTS "{req.table_name}"')
        db.execute(stmt)
        db.commit()
        return DbOperationResponse(
            status="Success",
            message=f"Table '{req.table_name}' dropped successfully.",
            affected_rows=0
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to drop table: {str(e)}")
    finally:
        db.close()

@router.post("/db/reset", response_model=DbOperationResponse)
def reset_database_data():
    """Resets the university domain database back to original sample state."""
    try:
        reset_university_data()
        return DbOperationResponse(
            status="Success",
            message="University database schema and sample data reset successfully.",
            affected_rows=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset database: {str(e)}")

@router.get("/sample-queries", response_model=List[Dict[str, Any]])
def get_sample_queries():
    """Returns curated Natural Language queries for demonstration."""
    return [
        {
            "category": "Database Mutation (Insert Student Tuple)",
            "query": "insert into students (name, email, dept_id, admission_year, cgpa) values ('Aarush Verma', 'aarush.verma@nexus.edu', 1, 2024, 9.2)",
            "expected_algorithm_fit": "DML Insert Dispatch",
            "priority": 7
        },
        {
            "category": "Conversational Insert (NLP to SQL)",
            "query": "insert student Riya Sen with email riya.sen@nexus.edu, cgpa 8.9, dept 2 into students",
            "expected_algorithm_fit": "DML Insert Dispatch",
            "priority": 6
        },
        {
            "category": "Baseline Aggregation (FCFS)",
            "query": "Show total number of students",
            "expected_algorithm_fit": "FCFS (Queue FIFO Order)",
            "priority": 3
        },
        {
            "category": "Priority Candidate (Critical Admin)",
            "query": "Show department budgets ordered by highest budget",
            "expected_algorithm_fit": "Priority (Priority Level = 9)",
            "priority": 9
        },
        {
            "category": "Filtering & Selection (Round Robin)",
            "query": "Find students with CGPA greater than 8.5",
            "expected_algorithm_fit": "Round Robin (Time Quantum = 2)",
            "priority": 5
        },
        {
            "category": "Complex Multi-Join & Views",
            "query": "Show student performance details for marks greater than 75",
            "expected_algorithm_fit": "Resource-Aware (Needs 128MB RAM)",
            "priority": 7
        },
        {
            "category": "Database Mutation (Delete Row via NL)",
            "query": "Delete student with student_id 40",
            "expected_algorithm_fit": "DML Deletion Dispatch",
            "priority": 6
        },
        {
            "category": "Security Guardrail Violation Test",
            "query": "DROP TABLE nexus_jobs; SELECT * FROM nexus_users;",
            "expected_algorithm_fit": "Safety Validator Reject (Protected System Table)",
            "priority": 1
        }
    ]
