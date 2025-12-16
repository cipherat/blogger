from typing import List
from datetime import date

from fastapi import APIRouter, UploadFile, File, Form, Depends, Request, HTTPException, status, Query
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from pydantic import BaseModel, Field

from app.services.get_blog import GetBlogService, get_get_blog_service
from app.services.get_page_blogs import GetPageBlogsService, get_get_page_blogs_service
from app.services.get_blogs import GetBlogsService, get_get_blogs_service
from app.services.register_blog import RegisterBlogService, get_register_blog_service

from app.contracts.get_blog import GetBlogResponse
from app.contracts.get_page_blogs import GetPageBlogsResponse
from app.contracts.get_blogs import GetBlogsResponse
from app.contracts.register_blog import RegisterBlogRequest, RegisterBlogResponse

from app.enums.enums import BlogState


router = APIRouter(
    prefix="/blogs",
    tags=["Blog Management"],
)

templates = Jinja2Templates(directory="templates")

@router.get("/{year}/{month}/{day}/{title}", status_code=status.HTTP_200_OK)
async def get_blog_by_permalink(
    year: str,
    month: str,
    day: str,
    title: str,
    service: GetBlogService = Depends(get_get_blog_service),
) -> GetBlogResponse:
    try:
        result = service.run(year, month, day, title)
        return GetBlogResponse(
            status=result.get("status", "empty"),
            blog=result.get("blog", None),
            message=result.get("message", f"No blogs found."),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )

@router.get("/", name="page_blogs", response_model=GetPageBlogsResponse, status_code=status.HTTP_200_OK)
async def get_page_blogs(
    request: Request,
    page: int = Query(1, ge=1, description="..."),
    limit: int = Query(20, ge=1, le=100, description="..."),
    service: GetPageBlogsService = Depends(get_get_page_blogs_service),
) -> GetPageBlogsResponse:
    try:
        result = service.run(page, limit)

        context = {
            "request": request,
            "blogs": result.get("blogs", []),
            "page_data": result,
            "current_page": result.get("page", 1),
        }
        
        return templates.TemplateResponse("index.html", context)

        # return GetPageBlogsResponse(
        #     status=result.get("status", "empty"),
        #     blogs=result.get("blogs"),
        #     total_count=result.get("total_count"),
        #     page=result.get("page"),
        #     limit=result.get("limit"),
        #     total_pages=result.get("total_pages"),
        #     has_next=result.get("has_next"),
        #     has_previous=result.get("has_previous"),
        #     message=result.get("message", "No blogs found (empty result)."),
        # )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )
    
"""
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
"""

"""
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
"""

@router.get("/register", name="register_form", status_code=status.HTTP_200_OK)
async def get_register_form(request: Request):
    context = {
        "request": request,
        "states": BlogState.list_values(),
        "errors": {},
        "form_data": {} 
    }
    return templates.TemplateResponse("register.html", context)

@router.post("/register", name="register_submission", response_model=RegisterBlogResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    title: str = Form(...),
    category: str = Form(...),
    keywords_csv: str = Form(..., description="Comma-separated string of keywords"),
    references_csv: str = Form(""),
    published_at_str: str = Form(..., description="Date string (YYYY-MM-DD)"),
    content_file: str = Form(...),
    state: BlogState = Form(BlogState.published),
    service: RegisterBlogService = Depends(get_register_blog_service),
) -> RegisterBlogResponse:
    context = {
        "request": request,
        "states": BlogState.list_values(),
        "errors": {},
    }
    
    raw_form_data = locals().copy()    
    try:
        keywords_list = [k.strip() for k in keywords_csv.split(',') if k.strip()]
        references_list = [r.strip() for r in references_csv.split(',') if r.strip()]

        try:
            published_date = date.fromisoformat(published_at_str)
        except ValueError:
            context["errors"]["published_at"] = "Invalid date format. Use YYYY-MM-DD."
            context["form_data"] = {
                "title": title, "category": category, "keywords": keywords_list,
                "references": references_list, "content_file": content_file,
                "state": state.value, "published_at_str": published_at_str
            }
            return templates.TemplateResponse("register.html", context, status_code=status.HTTP_400_BAD_REQUEST)
            
        request_model = RegisterBlogRequest(
            title=title,
            category=category,
            keywords=keywords_list,
            published_at=published_date,
            content_file=content_file,
            references=references_list,
            state=state,
        )
        result = service.run(request_model)
        
        if result.get("status") == "success":
             return RedirectResponse(url=request.url_for("page_blogs"), status_code=status.HTTP_303_SEE_OTHER)

        context["errors"]["submission"] = result.get("message", "Registration failed due to a service error.")
        context["form_data"] = request_model.model_dump()
        return templates.TemplateResponse("register.html", context, status_code=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during registration: {e}",
        )
