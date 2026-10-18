class SchemaPromptBuilder:
    """
    Formats the University Database DDL and view context for LLM prompt injection.
    Excludes internal system tables (nexus_users, nexus_jobs, nexus_queries).
    """
    
    SYSTEM_INSTRUCTION = """
You are an expert SQLite/PostgreSQL Database Administrator and Text-to-SQL Translator for Project NEXUS.
Your sole job is to translate Natural Language questions and commands into executable SQL queries based strictly on the provided database schema.

CRITICAL RULES:
1. Generate valid SELECT, WITH, INSERT, UPDATE, or DELETE queries.
2. Do NOT generate destructive DDL/DCL statements such as DROP, ALTER, TRUNCATE, CREATE, GRANT, or REVOKE.
3. Never access internal system tables (nexus_users, nexus_queries, nexus_jobs).
4. Use exact column names and table/view names from the schema context.
5. Output ONLY the raw SQL statement inside ```sql ... ``` code block. Do NOT include markdown explanations.
6. If the request cannot be fulfilled by the schema, respond with: -- ERROR: Unsupported or ambiguous query request.
"""

    SCHEMA_CONTEXT = """
TARGET DATABASE SCHEMA:

Table `departments`:
  - dept_id (INTEGER PRIMARY KEY)
  - dept_name (VARCHAR)
  - building (VARCHAR)
  - budget (FLOAT)

Table `students`:
  - student_id (INTEGER PRIMARY KEY)
  - name (VARCHAR)
  - email (VARCHAR)
  - dept_id (INTEGER, FOREIGN KEY -> departments.dept_id)
  - admission_year (INTEGER)
  - cgpa (FLOAT)

Table `courses`:
  - course_id (INTEGER PRIMARY KEY)
  - course_code (VARCHAR)
  - course_name (VARCHAR)
  - credits (INTEGER)
  - dept_id (INTEGER, FOREIGN KEY -> departments.dept_id)

Table `enrolments`:
  - enrolment_id (INTEGER PRIMARY KEY)
  - student_id (INTEGER, FOREIGN KEY -> students.student_id)
  - course_id (INTEGER, FOREIGN KEY -> courses.course_id)
  - semester (VARCHAR)
  - year (INTEGER)

Table `marks`:
  - mark_id (INTEGER PRIMARY KEY)
  - enrolment_id (INTEGER, FOREIGN KEY -> enrolments.enrolment_id)
  - exam_type (VARCHAR) -- 'Midterm', 'Endterm', 'Assignment'
  - marks_obtained (FLOAT)
  - max_marks (FLOAT)

View `vw_student_performance`:
  - student_id, student_name, cgpa, admission_year, dept_name, course_name, exam_type, marks_obtained, max_marks
"""

    @classmethod
    def build_prompt(cls, nl_query: str) -> str:
        return f"{cls.SCHEMA_CONTEXT}\nNatural Language User Question: \"{nl_query}\"\nGenerated SQL Query:"

