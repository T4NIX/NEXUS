import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "NEXUS — AI Natural Language to SQL with OS Process Scheduling"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    ENV: str = os.getenv("ENV", "development")
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Gemini AI API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # Database Settings
    SYSTEM_DATABASE_URL: str = os.getenv("SYSTEM_DATABASE_URL", "sqlite:///./nexus_system.db")
    UNIVERSITY_DATABASE_URL: str = os.getenv("UNIVERSITY_DATABASE_URL", "sqlite:///./nexus_university.db")
    
    # OS Scheduling Defaults
    DEFAULT_SCHEDULER_ALGORITHM: str = os.getenv("DEFAULT_SCHEDULER_ALGORITHM", "FCFS")  # FCFS, PRIORITY, RR
    QUANTUM_TICKS: int = int(os.getenv("QUANTUM_TICKS", "2"))
    MAX_CONCURRENT_WORKERS: int = int(os.getenv("MAX_CONCURRENT_WORKERS", "3"))

settings = Settings()
