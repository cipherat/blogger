import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from app.gateways.postgres.client import PostgresClient
from app.controllers.blog import router as blog_router


API_VERSION = "v1.0.0"
API_PREFIX = f"/api/{API_VERSION.split('.')[0]}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_client = PostgresClient(
        dbname=os.getenv("DB_NAME", "blogger_db"),
        user=os.getenv("DB_USER", "blogger_user"),
        password=os.getenv("DB_PASS", "your_password"),
        host=os.getenv("DB_HOST", "database"),
        port=os.getenv("DB_PORT", 5432)
    )
    yield
    app.state.db_client.close_all()

app = FastAPI(
    title="Blog Management Tool API",
    version=API_VERSION,
    root_path=API_PREFIX,
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(blog_router)

@app.get("/", include_in_schema=False)
async def root():
    return {"message": f"Blog Management API ({API_VERSION}) running. Access /docs for documentation."}

# To run the application, use the command: 
# uvicorn main:app --reload --port 6969
