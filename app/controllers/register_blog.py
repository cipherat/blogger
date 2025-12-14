from typing import List

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.contracts.register_blog import RegisterBlogRequest

from app.services.register_blog import RegisterBlogService, get_register_blog_service


router = APIRouter(
    prefix="/blog",
    tags=["Blog Management"],
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_blog(
    request: RegisterBlogRequest,
    service: RegisterBlogService = Depends(get_register_blog_service),
):
    """
    Registers new blog metadata and handles file uploads.
    """
    try:
        service.run(request)
        return {
            "message": "Blog metadata and files received successfully",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
