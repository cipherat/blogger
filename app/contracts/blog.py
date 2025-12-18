from typing import List, Optional, Any
from pydantic import BaseModel, Field
from datetime import date

from app.enums.enums import BlogState
from app.models.blog import Blog


class BaseResponse(BaseModel):
    status: str = Field(..., description="The status of the response (success/error).")
    message: str = Field(..., description="Response detailed message.")

class GetBlogResponse(BaseResponse):
    blog: Optional[Blog.Schema] = Field(None, description="The blog data.")

class GetBlogsResponse(BaseResponse):
    blogs: List[Blog.Schema] = Field(default_factory=list, description="List of all blogs.")

class GetPageBlogsResponse(BaseResponse):
    blogs: List[Blog.Schema] = Field(default_factory=list, description="List of paged blogs.")
    total_count: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_previous: bool

class RegisterBlogRequest(BaseModel):
    title: str = Field(..., max_length=255)
    category: str = Field(..., max_length=50)
    keywords: List[str]
    published_at: Optional[date] = Field(None)
    content_file: str
    references: List[str] = Field(default_factory=list)
    state: BlogState = Field(BlogState.PUBLISHED)

class RegisterBlogResponse(BaseResponse):
    id: Optional[str] = Field(None, description="The unique ID of the registered blog.")

class UpdateBlogRequest(BaseModel):
    title: str
    category: str
    keywords: List[str]
    published_at: date
    content_file: str
    references: List[str]
    state: BlogState

class ActionResponse(BaseResponse):
    pass
