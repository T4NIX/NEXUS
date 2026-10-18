import random
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.dbms.connection import university_engine, UniversitySessionLocal, system_engine, SystemSessionLocal
from app.models.db_models import Base, Department, Student, Course, Enrolment, Mark, User

def seed_university_data(force: bool = False):
    """Populates the University database with sample domain data and creates DB views."""
    Base.metadata.create_all(bind=university_engine)
    db: Session = UniversitySessionLocal()
    
    try:
        # Check if already seeded unless forced
        if not force and db.query(Department).count() > 0:
            return
        
        # 1. Departments
        depts_data = [
            ("Computer Science & Engineering", "Tech Block A", 2500000.0),
            ("Electrical & Electronics", "Tech Block B", 2000000.0),
            ("Mechanical Engineering", "Workshop Block C", 1800000.0),
            ("Civil Engineering", "Infra Block D", 1500000.0),
            ("Data Science & AI", "Innovation Lab E", 3000000.0)
        ]
        
        dept_objs = []
        for name, bldg, budget in depts_data:
            d = Department(dept_name=name, building=bldg, budget=budget)
            db.add(d)
            dept_objs.append(d)
        
        db.commit()
        
        # 2. Courses
        courses_data = [
            ("CS101", "Database Management Systems", 4, 1),
            ("CS102", "Operating Systems Architecture", 4, 1),
            ("CS103", "Data Structures & Algorithms", 4, 1),
            ("AI201", "Artificial Intelligence & Machine Learning", 4, 5),
            ("AI202", "Natural Language Processing", 3, 5),
            ("EE101", "Digital Electronics & Microprocessors", 3, 2),
            ("ME101", "Thermodynamics & Heat Transfer", 4, 3),
            ("CE101", "Structural Engineering & Mechanics", 4, 4),
        ]
        
        course_objs = []
        for code, name, credits, d_id in courses_data:
            c = Course(course_code=code, course_name=name, credits=credits, dept_id=d_id)
            db.add(c)
            course_objs.append(c)
            
        db.commit()
        
        # 3. Students
        first_names = ["Aarav", "Ananya", "Rohan", "Priya", "Vikram", "Neha", "Aditya", "Sneha", "Karan", "Pooja",
                       "Siddharth", "Ishita", "Rahul", "Divya", "Arjun", "Kavya", "Manish", "Riya", "Varun", "Meera"]
        last_names = ["Sharma", "Verma", "Singh", "Gupta", "Patel", "Reddy", "Rao", "Kumar", "Joshi", "Nair"]
        
        student_objs = []
        for i in range(1, 41):
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            name = f"{fn} {ln}"
            email = f"{fn.lower()}.{ln.lower()}{i}@university.edu"
            d_id = random.randint(1, 5)
            year = random.choice([2021, 2022, 2023, 2024])
            cgpa = round(random.uniform(6.5, 9.8), 2)
            
            s = Student(name=name, email=email, dept_id=d_id, admission_year=year, cgpa=cgpa)
            db.add(s)
            student_objs.append(s)
            
        db.commit()
        
        # 4. Enrolments & Marks
        exam_types = ["Midterm", "Endterm", "Assignment"]
        enrolment_objs = []
        
        for s in student_objs:
            # Enrol each student in 2-3 courses
            selected_courses = random.sample(course_objs, k=random.randint(2, 3))
            for c in selected_courses:
                e = Enrolment(student_id=s.student_id, course_id=c.course_id, semester="Fall", year=2024)
                db.add(e)
                db.flush()
                enrolment_objs.append(e)
                
                # Add marks for each exam type
                for etype in exam_types:
                    max_m = 100.0 if etype == "Endterm" else (50.0 if etype == "Midterm" else 20.0)
                    obtained = round(random.uniform(max_m * 0.5, max_m * 0.98), 1)
                    m = Mark(enrolment_id=e.enrolment_id, exam_type=etype, marks_obtained=obtained, max_marks=max_m)
                    db.add(m)
                    
        db.commit()
        
        # 5. Create Database Views for AI Context Isolation
        with university_engine.connect() as conn:
            conn.execute(text("""
                CREATE VIEW IF NOT EXISTS vw_student_performance AS
                SELECT 
                    s.student_id,
                    s.name AS student_name,
                    s.cgpa,
                    s.admission_year,
                    d.dept_name,
                    c.course_name,
                    m.exam_type,
                    m.marks_obtained,
                    m.max_marks
                FROM students s
                JOIN departments d ON s.dept_id = d.dept_id
                JOIN enrolments e ON s.student_id = e.student_id
                JOIN courses c ON e.course_id = c.course_id
                JOIN marks m ON e.enrolment_id = m.enrolment_id;
            """))
            conn.commit()
            
    except Exception as ex:
        db.rollback()
        print(f"Error seeding university DB: {ex}")
def reset_university_data():
    """Drops domain tables/views and freshly reseeds all university sample data."""
    with university_engine.connect() as conn:
        conn.execute(text("DROP VIEW IF EXISTS vw_student_performance;"))
        conn.execute(text("DROP TABLE IF EXISTS marks;"))
        conn.execute(text("DROP TABLE IF EXISTS enrolments;"))
        conn.execute(text("DROP TABLE IF EXISTS courses;"))
        conn.execute(text("DROP TABLE IF EXISTS students;"))
        conn.execute(text("DROP TABLE IF EXISTS departments;"))
        conn.commit()
    seed_university_data(force=True)

def seed_system_data():
    """Seed initial system admin users."""
    Base.metadata.create_all(bind=system_engine)
    db: Session = SystemSessionLocal()
    try:
        if db.query(User).count() == 0:
            user = User(user_id="user_1", username="Student Explorer", email="student@nexus.edu", role="student")
            admin = User(user_id="admin_1", username="System Administrator", email="admin@nexus.edu", role="admin")
            db.add(user)
            db.add(admin)
            db.commit()
    except Exception as ex:
        db.rollback()
        print(f"Error seeding system DB: {ex}")
    finally:
        db.close()
