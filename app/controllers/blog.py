from typing import Optional, List
from datetime import date

from fastapi import APIRouter, Form, Depends, Request, HTTPException, status, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError

from app.services.blog import BlogService, get_blog_service
from app.contracts.blog import (
    GetBlogResponse,
    GetPageBlogsResponse,
    RegisterBlogRequest,
    RegisterBlogResponse,
    UpdateBlogRequest,
    ActionResponse
)
from app.enums.enums import BlogState


router = APIRouter(
    prefix="/blogs",
    tags=["Blog Management"],
)

templates = Jinja2Templates(directory="templates")


@router.get("/", name="page_blogs")
async def get_page_blogs(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(7, ge=1, le=100),
    state: Optional[BlogState] = BlogState.PUBLISHED,
    service: BlogService = Depends(get_blog_service),
):
    result = service.get_page(page, limit, state=state)

    if "text/html" in request.headers.get("accept", ""):
        context = {
            "request": request,
            "blogs": result.get("blogs", []),
            "page_data": result,
            "current_page": page,
        }
        return templates.TemplateResponse("index.html", context)

    return GetPageBlogsResponse(**result)


@router.get("/{year}/{month}/{day}/{slug}", response_model=GetBlogResponse)
async def get_blog_by_permalink(
    year: str, month: str, day: str, slug: str,
    service: BlogService = Depends(get_blog_service),
):
    result = service.get_one(year, month, day, slug)
    if result["status"] == "error":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["message"])
    
    return GetBlogResponse(**result)


@router.get("/id/{blog_id}", response_model=GetBlogResponse)
async def get_blog_by_id(
    blog_id: str,
    service: BlogService = Depends(get_blog_service)
):
    result = service.get_by_id(blog_id)
    if result["status"] == "error":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["message"])
    
    return GetBlogResponse(**result)


@router.get("/register", response_class=HTMLResponse)
async def get_register_form(request: Request):
    context = {
        "request": request,
        "states": BlogState.list_values(),
        "errors": {},
        "form_data": {},
    }
    return templates.TemplateResponse("register.html", context)


@router.post("/register", name="register_submission")
async def register(
    request: Request,
    title: str = Form(...),
    category: str = Form(...),
    keywords_csv: str = Form(...),
    references_csv: str = Form(""),
    published_at_str: str = Form(...),
    content_file: str = Form(...),
    state: BlogState = Form(BlogState.PUBLISHED),
    service: BlogService = Depends(get_blog_service),
):
    try:
        keywords = [k.strip() for k in keywords_csv.split(',') if k.strip()]
        references = [r.strip() for r in references_csv.split(',') if r.strip()]
        published_date = date.fromisoformat(published_at_str)

        request_model = RegisterBlogRequest(
            title=title, category=category, keywords=keywords,
            published_at=published_date, content_file=content_file,
            references=references, state=state,
        )

        result = service.register(request_model)        
        if result["status"] == "success":
            if "text/html" in request.headers.get("accept", ""):
                return RedirectResponse(url=request.url_for("page_blogs"), status_code=status.HTTP_303_SEE_OTHER)
            return RegisterBlogResponse(**result)
            
        raise ValueError(result["message"])

    except Exception as e:
        if "text/html" in request.headers.get("accept", ""):
            context = {
                "request": request,
                "states": BlogState.list_values(),
                "errors": {"submission": str(e)},
                "form_data": locals(),
            }
            return templates.TemplateResponse("register.html", context, status_code=status.HTTP_400_BAD_REQUEST)
        
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{blog_id}", response_model=ActionResponse)
async def update_blog(
    blog_id: str,
    update_data: UpdateBlogRequest,
    service: BlogService = Depends(get_blog_service)
):
    result = service.update_blog(blog_id, update_data)
    if result["status"] == "error":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])
    
    return ActionResponse(**result)


@router.delete("/{blog_id}", response_model=ActionResponse)
async def delete_blog(
    blog_id: str,
    service: BlogService = Depends(get_blog_service)
):
    result = service.delete(blog_id)
    if result["status"] == "error":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["message"])
    
    return ActionResponse(**result)
