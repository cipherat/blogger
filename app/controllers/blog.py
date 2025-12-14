from typing import List

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.services.get_blog import GetBlogService, get_get_blog_service
from app.services.get_blogs import GetBlogsService, get_get_blogs_service
from app.services.register_blog import RegisterBlogService, get_register_blog_service

from app.contracts.get_blog import GetBlogResponse
from app.contracts.get_blogs import GetBlogsResponse
from app.contracts.register_blog import RegisterBlogRequest, RegisterBlogResponse


router = APIRouter(
    prefix="/blogs",
    tags=["Blog Management"],
)

@router.get("/{blog_id}", response_model=GetBlogResponse, status_code=status.HTTP_200_OK)
async def get_blog_by_id(
    blog_id: str,
    service: GetBlogService = Depends(get_get_blog_service)
) -> GetBlogResponse:
        try:
            result = service.run(blog_id)
            return GetBlogResponse(
                status=result.get("status", "empty"),
                blog=result.get("blog", None),
                message=result.get("message", f"No blogs found with ID ({blog_id})."),
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {e}",
            )
    

@router.get("/", response_model=GetBlogsResponse, status_code=status.HTTP_200_OK)
async def get_all_blogs(
    service: GetBlogsService = Depends(get_get_blogs_service)
) -> GetBlogsResponse:
    try:
        result = service.run()
        return GetBlogsResponse(
            status=result.get("status", "empty"),
            blogs=result.get("blogs", None),
            message=result.get("message", "No blogs found (empty result)."),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )

@router.post("/register", response_model=RegisterBlogResponse, status_code=status.HTTP_201_CREATED)
async def register_blog(
    request: RegisterBlogRequest,
    service: RegisterBlogService = Depends(get_register_blog_service),
) -> RegisterBlogResponse:
    try:
        result = service.run(request)
        return RegisterBlogResponse(
            status=result.get("status", "failure"),
            id=result.get("id", -1),
            message=result.get("message", "Failed to register Blog metadata."),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )
