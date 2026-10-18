import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.dbms.connection import init_databases
from app.dbms.seed_data import seed_university_data, seed_system_data
from app.os.worker_cluster import worker_cluster

from app.api.routes_query import router as query_router
from app.api.routes_scheduler import router as scheduler_router
from app.api.routes_system import router as system_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Lifespan
    print("=========================================================")
    print(f"  Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print("=========================================================")
    init_databases()
    seed_system_data()
    seed_university_data()
    
    # Start Worker Cluster
    worker_cluster.start()
    print("[Worker Cluster] 3 Asynchronous Worker Threads Initialized.")
    print("---------------------------------------------------------")
    print(f"  Web Dashboard: http://localhost:{settings.PORT}")
    print(f"  API Docs:      http://localhost:{settings.PORT}/docs")
    print("=========================================================")
    
    yield
    
    # Shutdown Lifespan
    print("[Worker Cluster] Stopping Worker Threads...")
    worker_cluster.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Natural Language to SQL Translation with OS Process Scheduling and DBMS ACID Integrity",
    lifespan=lifespan
)

# CORS Configuration for Frontend Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(query_router, prefix=settings.API_PREFIX)
app.include_router(scheduler_router, prefix=settings.API_PREFIX)
app.include_router(system_router, prefix=settings.API_PREFIX)

@app.get("/health")
def health_check():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "active_scheduler": "Active",
        "worker_threads": len(worker_cluster.workers)
    }

# Serve Frontend static assets if dist exists
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(frontend_dist, "index.html"))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=False)

