import pytest
import time
from fastapi.testclient import TestClient
from app.main import app

def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "online"

def test_query_submit_pipeline():
    with TestClient(app) as client:
        payload = {
            "nl_query": "Show total number of students",
            "priority": 7,
            "user_id": "test_user"
        }
        response = client.post("/api/v1/query/submit", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        job_id = data["job_id"]
        assert job_id >= 100

        pcb_response = client.get(f"/api/v1/query/{job_id}")
        assert pcb_response.status_code == 200
        pcb_data = pcb_response.json()
        assert pcb_data["job_id"] == job_id
        assert pcb_data["nl_query"] == payload["nl_query"]

def test_insert_query_pipeline():
    with TestClient(app) as client:
        uid = int(time.time() * 1000) % 100000
        test_email = f"pipeline_{uid}@test.edu"
        payload = {
            "nl_query": f"insert into students (name, email, dept_id, admission_year, cgpa) values ('Pipeline Test {uid}', '{test_email}', 1, 2024, 9.5)",
            "priority": 8,
            "user_id": "integration_user"
        }
        response = client.post("/api/v1/query/submit", json=payload)
        assert response.status_code == 200
        data = response.json()
        job_id = data["job_id"]

        # Wait for worker thread to process
        for _ in range(25):
            time.sleep(0.2)
            pcb_res = client.get(f"/api/v1/query/{job_id}")
            if pcb_res.status_code == 200 and pcb_res.json()["status"] in ["COMPLETED", "FAILED"]:
                break

        final_pcb = client.get(f"/api/v1/query/{job_id}").json()
        assert final_pcb["status"] == "COMPLETED"
        assert final_pcb["safety_valid"] is True
        assert final_pcb["execution_result"] is not None

def test_insert_row_direct_endpoint():
    with TestClient(app) as client:
        uid = int(time.time() * 1000) % 100000
        payload = {
            "table_name": "departments",
            "row_data": {
                "dept_name": f"Quantum Computing Dept {uid}",
                "building": "Quantum Hall Q",
                "budget": 4500000.0
            }
        }
        response = client.post("/api/v1/system/db/insert-row", json=payload)
        assert response.status_code == 200
        res_data = response.json()
        assert res_data["status"] == "Success"
        assert "departments" in res_data["message"]

def test_scheduler_metrics():
    with TestClient(app) as client:
        response = client.get("/api/v1/scheduler/metrics")
        assert response.status_code == 200
        metrics = response.json()
        assert "active_algorithm" in metrics
        assert "avg_turnaround_time" in metrics

def test_dbms_schema_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/v1/system/db-schema")
        assert response.status_code == 200
        schema = response.json()
        assert len(schema["tables"]) > 0
        assert "vw_student_performance" in schema["views"]
