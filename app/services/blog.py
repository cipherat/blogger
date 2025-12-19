from typing import Any, Dict, List, Optional
import os
from datetime import date
from fastapi import Depends

from app.repositories.blog import get_blog_repository
from app.models.blog import Blog, get_blog_model
from app.models.dates import DatesModel
from app.enums.enums import BlogState

from app.contracts.blog import (
    GetBlogResponse,
    GetBlogsResponse,
    GetPageBlogsResponse,
    RegisterBlogRequest,
    RegisterBlogResponse,
    UpdateBlogRequest,
    ActionResponse,
)

class BlogService:
    def __init__(self, model: Blog = Depends(get_blog_model)):
        self.model = model

    def get_one(self, year: str, month: str, day: str, slug: str) -> Dict[str, Any]:
        blog_schema = self.model.find_by_permalink(year, month, day, slug)        
        if not blog_schema:
            return {"status": "error", "message": "Blog not found"}

        file_path = blog_schema.content_file
        try:
            if not os.path.exists(file_path):
                return {
                    "status": "error",
                    "message": f"Source file missing: {blog_schema.content_file}",
                }
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            return {
                "status": "success",
                "blog": blog_schema,
                "content": content,
                "message": "Source content loaded successfully",
            }
        except Exception as e:
            return {"status": "error", "message": f"Filesystem Error: {str(e)}"}

    def get_by_id(self, blog_id: str) -> Dict[str, Any]:
        blog = self.model.find_by_id(blog_id)
        return {
            "status": "success" if blog else "error",
            "blog": blog,
            "message": "Blog found" if blog else "Blog not found",
        }

    def get_all(self) -> Dict[str, Any]:
        blogs = self.model.get_all()
        return {
            "status": "success",
            "blogs": blogs,
            "message": f"Successfully retrieved {len(blogs)} blogs",
        }

    def get_page(self, page: int, limit: int, state: Optional[BlogState] = None) -> Dict[str, Any]:
        data = self.model.get_page(page, limit, state=state)

        blogs = data.get("blogs", [])
        total_count = data.get("total_count", 0)
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        
        return {
            "status": "success",
            "blogs": blogs,
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
            "message": "Successfully retrieved paged blogs",
        }

    def register(self, request: RegisterBlogRequest) -> Dict[str, Any]:
        file_metadata = self._extract_file_metadata(request.content_file)
        
        dates = DatesModel(
            created_at=date.fromtimestamp(file_metadata['created_at_ts']),
            published_at=request.published_at,
            last_update=date.fromtimestamp(file_metadata['last_update_ts']),
        )

        blog_data = self.model.Schema(
            id=file_metadata['id'],
            title=request.title,
            category=request.category,
            keywords=request.keywords,
            dates=dates,
            content_file=request.content_file,
            references=request.references,
            state=request.state,
        )
        
        self.model.save(blog_data)
        return {
            "status": "success",
            "id": blog_data.id,
            "message": f"Blog '{blog_data.title}' registered successfully",
        }

    def update_blog(self, blog_id: str, request: UpdateBlogRequest) -> Dict[str, Any]:
        existing = self.model.find_by_id(blog_id)
        if not existing:
            return {"status": "error", "message": "Cannot update: Blog not found"}

        updated_data = self.model.Schema(
            id=blog_id,
            title=request.title,
            category=request.category,
            keywords=request.keywords,
            dates=DatesModel(
                created_at=existing.dates.created_at,
                published_at=request.published_at,
                last_update=date.today(),
            ),
            content_file=request.content_file,
            references=request.references,
            state=request.state,
        )

        self.model.update(blog_id, updated_data)
        return {"status": "success", "message": "Blog updated successfully"}

    def delete(self, blog_id: str) -> Dict[str, Any]:
        if not self.model.find_by_id(blog_id):
            return {"status": "error", "message": "Delete failed: Blog not found"}
            
        self.model.repository.delete(blog_id)
        return {"status": "success", "message": f"Blog {blog_id} deleted successfully"}

    def _extract_file_metadata(self, content_path: str) -> Dict[str, Any]:
        if not os.path.exists(content_path):
            raise FileNotFoundError(f"Content file not found at path: {content_path}")
        
        created_at_ts = int(os.path.getctime(content_path))
        last_update_ts = int(os.path.getmtime(content_path))
        unique_id = str(int(created_at_ts * 1000000))
        
        return {
            "id": unique_id,
            "created_at_ts": created_at_ts,
            "last_update_ts": last_update_ts,
        }


def get_blog_service(service: BlogService = Depends(BlogService)) -> BlogService:
    return service
