import pytest
from app.ai.prompt_templates import SchemaPromptBuilder
from app.ai.translator import AITranslator

def test_schema_prompt_builder():
    prompt = SchemaPromptBuilder.build_prompt("Show top 5 students by CGPA")
    assert "TARGET DATABASE SCHEMA" in prompt
    assert "Show top 5 students by CGPA" in prompt
    assert "students" in prompt
    assert "INSERT INTO" in SchemaPromptBuilder.SYSTEM_INSTRUCTION

def test_ai_mock_translator_select():
    sql1 = AITranslator.translate("Show total number of students")
    assert "SELECT COUNT" in sql1.upper()
    assert "students" in sql1.lower()

    sql2 = AITranslator.translate("Show top 5 students by CGPA")
    assert "SELECT" in sql2.upper()
    assert "LIMIT 5" in sql2.upper() or "LIMIT" in sql2.upper()

def test_ai_translator_direct_insert():
    raw_sql = "INSERT INTO students (name, email, dept_id, admission_year, cgpa) VALUES ('Direct Student', 'direct@nexus.edu', 1, 2024, 8.8);"
    translated = AITranslator.translate(raw_sql)
    assert translated.upper().startswith("INSERT INTO STUDENTS")
    assert "Direct Student" in translated

def test_ai_translator_conversational_inserts():
    # 1. Student insert
    sql_student = AITranslator.translate("insert student Alice with email alice@nexus.edu, cgpa 9.2 into students")
    assert sql_student.upper().startswith("INSERT INTO STUDENTS")
    assert "Alice" in sql_student
    assert "alice@nexus.edu" in sql_student
    assert "9.2" in sql_student

    # 2. Tuple into students
    sql_tuple = AITranslator.translate("insert tuple into students")
    assert sql_tuple.upper().startswith("INSERT INTO STUDENTS")
    assert "VALUES" in sql_tuple.upper()

    # 3. Department insert
    sql_dept = AITranslator.translate("insert department Robotics in Tech Block with budget 250000 into departments")
    assert sql_dept.upper().startswith("INSERT INTO DEPARTMENTS")
    assert "Robotics" in sql_dept
    assert "250000" in sql_dept

    # 4. Course insert
    sql_course = AITranslator.translate("insert course CS201 Algorithms with 4 credits in dept 1 into courses")
    assert sql_course.upper().startswith("INSERT INTO COURSES")
    assert "CS201" in sql_course
    assert "Algorithms" in sql_course

    # 5. Enrolment insert
    sql_enrol = AITranslator.translate("insert new enrolment for student 5 in course 2")
    assert sql_enrol.upper().startswith("INSERT INTO ENROLMENTS")
    assert "5" in sql_enrol
    assert "2" in sql_enrol

    # 6. Marks insert
    sql_marks = AITranslator.translate("insert tuple into marks")
    assert sql_marks.upper().startswith("INSERT INTO MARKS")

def test_ai_translator_update():
    sql_upd = AITranslator.translate("update student 15 set cgpa = 9.5")
    assert sql_upd.upper().startswith("UPDATE STUDENTS")
    assert "9.5" in sql_upd
    assert "15" in sql_upd
