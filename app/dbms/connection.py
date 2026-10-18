import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.models.db_models import Base

# System Engine (stores users, queries, jobs metadata)
system_engine = create_engine(
    settings.SYSTEM_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.SYSTEM_DATABASE_URL else {}
)
SystemSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=system_engine)

# University Domain Engine (stores real target database data)
university_engine = create_engine(
    settings.UNIVERSITY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.UNIVERSITY_DATABASE_URL else {}
)
UniversitySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=university_engine)

def init_databases():
    """Initializes tables for System and University DBs."""
    Base.metadata.create_all(bind=system_engine)
    Base.metadata.create_all(bind=university_engine)

def get_system_db():
    """Dependency for getting system database session."""
    db = SystemSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_university_db():
    """Dependency for getting university database session."""
    db = UniversitySessionLocal()
    try:
        yield db
    finally:
        db.close()

