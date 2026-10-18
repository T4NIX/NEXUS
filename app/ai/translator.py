import os
import re
from app.config import settings
from app.ai.prompt_templates import SchemaPromptBuilder

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class AITranslator:
    """
    Handles Natural Language to SQL Translation using Google Gemini API
    with fallback to a smart Mock SQL Generator for offline testing.
    """

    @classmethod
    def translate(cls, nl_query: str) -> str:
        """Translates NL question to SQL string."""
        # Check if Gemini API key is available
        api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        
        if api_key and GEMINI_AVAILABLE:
            try:
                client = genai.Client(api_key=api_key)
                prompt = SchemaPromptBuilder.build_prompt(nl_query)
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SchemaPromptBuilder.SYSTEM_INSTRUCTION,
                        temperature=0.1,
                    ),
                )
                
                if response and response.text:
                    sql_match = re.search(r'```sql\s*(.*?)\s*```', response.text, re.DOTALL)
                    if sql_match:
                        return sql_match.group(1).strip()
                    return response.text.strip().strip(";").strip()
            except Exception as e:
                print(f"[AI Translator Warning] Gemini API failed: {e}. Using smart mock engine.")

        # Smart Fallback Mock Engine
        return cls._mock_translate(nl_query)

    @classmethod
    def _mock_translate(cls, nl_query: str) -> str:
        """Smart pattern-matching mock SQL generator with support for SELECT, INSERT, UPDATE, DELETE."""
        # 0. Raw SQL pass-through for direct query testing
        clean_raw = nl_query.strip().rstrip(";")
        upper_raw = clean_raw.upper()
        if upper_raw.startswith(("SELECT ", "WITH ", "INSERT INTO ", "DELETE FROM ", "UPDATE ")):
            return clean_raw + ";"

        q = nl_query.lower()
        
        # 1. INSERT / ADD queries
        if "insert" in q or "add" in q:
            if "student" in q:
                # Extract optional name in quotes or after student/name
                name_match = re.search(r'(?:name\s*(?:is|=|:)?\s*["\']?([a-zA-Z\s]+?)["\']?(?:,|$|\s+with|\s+and|\s+dept|\s+email|\s+cgpa))', nl_query, re.IGNORECASE)
                if not name_match:
                    name_match = re.search(r'(?:student|named)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', nl_query)
                name = name_match.group(1).strip() if name_match else "Alice Smith"
                
                # Extract optional email
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', nl_query)
                email = email_match.group(0) if email_match else f"{name.lower().replace(' ', '.')}@university.edu"
                
                # Extract optional cgpa
                cgpa_match = re.search(r'(?:cgpa|gpa|marks)\s*(?:is|=|:|to)?\s*(\d+(\.\d+)?)', q)
                cgpa = cgpa_match.group(1) if cgpa_match else "8.8"
                
                # Extract optional dept_id
                dept_match = re.search(r'(?:dept|department|dept_id)\s*(?:id|is|=|:|to)?\s*(\d+)', q)
                dept_id = dept_match.group(1) if dept_match else "1"
                
                # Extract optional admission year
                year_match = re.search(r'(?:year|admission_year)\s*(?:is|=|:|to)?\s*(20\d\d)', q)
                year = year_match.group(1) if year_match else "2024"
                
                return f"INSERT INTO students (name, email, dept_id, admission_year, cgpa) VALUES ('{name}', '{email}', {dept_id}, {year}, {cgpa});"

            if "department" in q:
                dept_match = re.search(r'(?:name|dept|department)\s*["\']?([a-zA-Z\s]+?)["\']?(?:,|$|\s+with|\s+in|\s+budget)', nl_query, re.IGNORECASE)
                dept_name = dept_match.group(1).strip() if dept_match else "Robotics"
                return f"INSERT INTO departments (dept_name, building, budget) VALUES ('{dept_name}', 'Tech Wing', 1200000.0);"

            if "course" in q:
                return "INSERT INTO courses (course_code, course_name, credits, dept_id) VALUES ('CS105', 'Data Structures', 4, 1);"

        # 2. DELETE / REMOVE queries
        if "delete" in q or "remove" in q:
            if "student" in q:
                id_match = re.search(r'(?:id|student_id|student)\s*(?:is|=|:)?\s*(\d+)', q)
                student_id = id_match.group(1) if id_match else "1"
                return f"DELETE FROM students WHERE student_id = {student_id};"
            if "course" in q:
                id_match = re.search(r'(?:id|course_id|course)\s*(?:is|=|:)?\s*(\d+)', q)
                course_id = id_match.group(1) if id_match else "1"
                return f"DELETE FROM courses WHERE course_id = {course_id};"
            if "department" in q:
                id_match = re.search(r'(?:id|dept_id|dept|department)\s*(?:is|=|:)?\s*(\d+)', q)
                dept_id = id_match.group(1) if id_match else "1"
                return f"DELETE FROM departments WHERE dept_id = {dept_id};"

        # 3. UPDATE / MODIFY queries
        if "update" in q or "modify" in q or "change" in q or "set" in q:
            if "student" in q:
                id_match = re.search(r'(?:id|student_id|student)\s*(?:is|=|:)?\s*(\d+)', q)
                student_id = id_match.group(1) if id_match else "1"
                if "cgpa" in q or "gpa" in q or "marks" in q:
                    cgpa_match = re.search(r'(?:to|cgpa|gpa|=|set)\s*(\d+(\.\d+)?)', q)
                    cgpa = cgpa_match.group(1) if cgpa_match else "9.5"
                    return f"UPDATE students SET cgpa = {cgpa} WHERE student_id = {student_id};"
                return f"UPDATE students SET email = 'updated.student@university.edu' WHERE student_id = {student_id};"
            if "department" in q:
                return "UPDATE departments SET budget = 1500000.0 WHERE dept_id = 1;"
        
        # 4. SELECT / READ queries
        if ("total number of students" in q) or ("count" in q and "students" in q):
            return "SELECT COUNT(*) AS total_students FROM students;"
            
        if "top" in q and "students" in q and ("cgpa" in q or "marks" in q or "gpa" in q):
            limit_match = re.search(r'top\s+(\d+)', q)
            limit = limit_match.group(1) if limit_match else "5"
            return f"SELECT student_id, name, cgpa, admission_year FROM students ORDER BY cgpa DESC LIMIT {limit};"
            
        if "department" in q or "departments" in q:
            if "budget" in q:
                return "SELECT dept_name, building, budget FROM departments ORDER BY budget DESC;"
            return "SELECT d.dept_name, COUNT(s.student_id) AS total_students FROM departments d LEFT JOIN students s ON d.dept_id = s.dept_id GROUP BY d.dept_id, d.dept_name;"
            
        if "course" in q or "courses" in q:
            return "SELECT course_code, course_name, credits FROM courses ORDER BY credits DESC;"
            
        if "performance" in q or ("marks" in q and "exam" in q):
            return "SELECT student_name, dept_name, course_name, exam_type, marks_obtained FROM vw_student_performance WHERE marks_obtained > 75 ORDER BY marks_obtained DESC LIMIT 10;"

        if "more than" in q or "greater than" in q or ">" in q:
            val_match = re.search(r'(\d+(\.\d+)?)', q)
            threshold = val_match.group(1) if val_match else "8.0"
            return f"SELECT student_id, name, cgpa, email FROM students WHERE cgpa > {threshold} ORDER BY cgpa DESC;"

        # Default query for generic questions
        return "SELECT s.student_id, s.name, s.cgpa, d.dept_name FROM students s JOIN departments d ON s.dept_id = d.dept_id LIMIT 10;"

