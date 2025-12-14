from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.register_blog import router as blog_router


API_VERSION = "v1.0.0"
API_PREFIX = f"/api/{API_VERSION.split('.')[0]}"

app = FastAPI(
    title="Blog Management Tool API",
    version=API_VERSION,
    root_path=API_PREFIX,
)

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
