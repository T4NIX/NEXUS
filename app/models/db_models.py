from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()

# ==========================================
# 1. SYSTEM DATABASE TABLES (OS & Job Core)
# ==========================================

class User(Base):
    __tablename__ = "nexus_users"
    
    user_id = Column(String(50), primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    role = Column(String(20), default="student")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    queries = relationship("QueryRecord", back_populates="user")

class QueryRecord(Base):
    __tablename__ = "nexus_queries"
    
    query_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("nexus_users.user_id"), nullable=False)
    nl_text = Column(Text, nullable=False)
    generated_sql = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="queries")
    job = relationship("JobRecord", back_populates="query_ref", uselist=False)

class JobRecord(Base):
    __tablename__ = "nexus_jobs"
    
    job_id = Column(Integer, primary_key=True)  # PID
    query_id = Column(Integer, ForeignKey("nexus_queries.query_id"), nullable=False)
    status = Column(String(30), default="NEW")  # NEW, READY, RUNNING, WAITING, COMPLETED, FAILED
    priority = Column(Integer, default=5)
    arrival_time = Column(Float, nullable=False)
    estimated_burst_time = Column(Integer, default=5)
    memory_mb = Column(Integer, default=64)
    start_time = Column(Float, nullable=True)
    completion_time = Column(Float, nullable=True)
    turnaround_time = Column(Float, nullable=True)
    waiting_time = Column(Float, nullable=True)
    worker_id = Column(String(30), nullable=True)
    is_safe = Column(Boolean, default=False)
    error_log = Column(Text, nullable=True)
    result_json = Column(Text, nullable=True)
    
    query_ref = relationship("QueryRecord", back_populates="job")


# ==========================================
# 2. UNIVERSITY DOMAIN TABLES (DBMS Target)
# ==========================================

class Department(Base):
    __tablename__ = "departments"
    
    dept_id = Column(Integer, primary_key=True, autoincrement=True)
    dept_name = Column(String(100), nullable=False, unique=True)
    building = Column(String(100), nullable=False)
    budget = Column(Float, nullable=False)
    
    students = relationship("Student", back_populates="department")
    courses = relationship("Course", back_populates="department")

class Student(Base):
    __tablename__ = "students"
    
    student_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    dept_id = Column(Integer, ForeignKey("departments.dept_id"), nullable=False)
    admission_year = Column(Integer, nullable=False)
    cgpa = Column(Float, nullable=False)
    
    department = relationship("Department", back_populates="students")
    enrolments = relationship("Enrolment", back_populates="student")

class Course(Base):
    __tablename__ = "courses"
    
    course_id = Column(Integer, primary_key=True, autoincrement=True)
    course_code = Column(String(20), nullable=False, unique=True)
    course_name = Column(String(150), nullable=False)
    credits = Column(Integer, nullable=False)
    dept_id = Column(Integer, ForeignKey("departments.dept_id"), nullable=False)
    
    department = relationship("Department", back_populates="courses")
    enrolments = relationship("Enrolment", back_populates="course")

class Enrolment(Base):
    __tablename__ = "enrolments"
    
    enrolment_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    semester = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False)
    
    student = relationship("Student", back_populates="enrolments")
    course = relationship("Course", back_populates="enrolments")
    marks = relationship("Mark", back_populates="enrolment")

class Mark(Base):
    __tablename__ = "marks"
    
    mark_id = Column(Integer, primary_key=True, autoincrement=True)
    enrolment_id = Column(Integer, ForeignKey("enrolments.enrolment_id"), nullable=False)
    exam_type = Column(String(50), nullable=False)  # Midterm, Endterm, Assignment
    marks_obtained = Column(Float, nullable=False)
    max_marks = Column(Float, default=100.0)
    
    enrolment = relationship("Enrolment", back_populates="marks")
