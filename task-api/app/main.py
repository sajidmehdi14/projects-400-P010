from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    create_db_and_tables()
    yield
    # Shutdown: Clean up resources (if needed)


app = FastAPI(title="Task API", version="1.0.0", lifespan=lifespan)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Task API"}
