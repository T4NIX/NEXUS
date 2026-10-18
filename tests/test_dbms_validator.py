import pytest
from app.dbms.query_validator import SQLQueryValidator
from app.dbms.cost_estimator import QueryCostEstimator

def test_valid_select_query():
    is_valid, msg = SQLQueryValidator.validate_sql("SELECT name, cgpa FROM students WHERE cgpa > 8.0;")
    assert is_valid is True

def test_allow_safe_domain_dml_and_ddl():
    # Safe INSERT
    is_valid, msg = SQLQueryValidator.validate_sql("INSERT INTO students (name, email, dept_id, admission_year, cgpa) VALUES ('Alice', 'alice@test.edu', 1, 2024, 9.0);")
    assert is_valid is True

    # Safe UPDATE
    is_valid, msg = SQLQueryValidator.validate_sql("UPDATE students SET cgpa = 9.5 WHERE student_id = 15;")
    assert is_valid is True

    # Safe DELETE
    is_valid, msg = SQLQueryValidator.validate_sql("DELETE FROM students WHERE student_id = 15;")
    assert is_valid is True

    # Safe DROP TABLE on domain table
    is_valid, msg = SQLQueryValidator.validate_sql("DROP TABLE marks;")
    assert is_valid is True

    # Safe ALTER TABLE DROP COLUMN
    is_valid, msg = SQLQueryValidator.validate_sql("ALTER TABLE departments DROP COLUMN budget;")
    assert is_valid is True

def test_reject_system_tables():
    # Must not allow access or drop of system tables
    is_valid, msg = SQLQueryValidator.validate_sql("SELECT * FROM nexus_users;")
    assert is_valid is False
    assert "restricted" in msg.lower()

    is_valid, msg = SQLQueryValidator.validate_sql("DROP TABLE nexus_jobs;")
    assert is_valid is False
    assert "restricted" in msg.lower()

    is_valid, msg = SQLQueryValidator.validate_sql("INSERT INTO nexus_users (user_id, username, email) VALUES ('u_fake', 'fake', 'fake@test.com');")
    assert is_valid is False
    assert "restricted" in msg.lower()

def test_reject_multi_statement_injection():
    is_valid, msg = SQLQueryValidator.validate_sql("SELECT * FROM students; DROP TABLE courses;")
    assert is_valid is False
    assert "multiple" in msg.lower()

def test_reject_dangerous_keywords():
    is_valid, msg = SQLQueryValidator.validate_sql("PRAGMA foreign_keys = OFF;")
    assert is_valid is False
    assert "forbidden" in msg.lower()

def test_cost_estimator():
    # Simple count -> 1 tick
    burst1, mem1 = QueryCostEstimator.estimate_cost("SELECT COUNT(*) FROM students")
    assert burst1 == 1

    # Complex join -> higher burst & memory
    sql2 = "SELECT s.name, d.dept_name, c.course_name FROM students s JOIN departments d ON s.dept_id = d.dept_id JOIN enrolments e ON s.student_id = e.student_id JOIN courses c ON e.course_id = c.course_id GROUP BY d.dept_name ORDER BY s.cgpa"
    burst2, mem2 = QueryCostEstimator.estimate_cost(sql2)
    assert burst2 > 3
    assert mem2 > 64
