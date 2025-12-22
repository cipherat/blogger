import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from app.config import get_settings
from app.gateways.postgres.client import PostgresClient
from app.controllers.blog import (
    public as blog_public,
    admin as blog_admin,
)


settings = get_settings()
API_VERSION = "v1.0.0"

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_client = PostgresClient(
        dbname=settings.BLOGGER_DB_NAME,
        user=settings.BLOGGER_DB_USER,
        password=settings.BLOGGER_DB_PASS,
        host=settings.BLOGGER_DB_HOST,
        port=settings.BLOGGER_DB_PORT,
    )
    yield
    app.state.db_client.close_all()

templates = Jinja2Templates(directory="templates")

app = FastAPI(
    title="Blog Management Tool API",
    version=API_VERSION,
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


if settings.BLOGGER_IS_ADMIN:
    app.include_router(blog_admin)

app.include_router(blog_public)

@app.get("/", include_in_schema=False)
async def root():
    return {"message": f"Blog Management API ({API_VERSION}) running. Access /docs for documentation."}

@app.get("/health")
def health_check():
    return {"status": "online", "user": "admin" if settings.BLOGGER_IS_ADMIN else "public"}

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: Exception):
    detail = getattr(exc, "detail", "RESOURCE_NOT_FOUND")
    return templates.TemplateResponse(
        "exceptions/404.html",
        {
            "request": request,
            "exception_detail": detail.upper(),
        },
        status_code=404,
    )

# To run the application, use the command: 
# uvicorn main:app --reload --port 6969
