from typing import Any, Dict
import os
from datetime import date

from app.repositories.blogs import BlogRepository, get_blog_repository
from app.models.blog import Blog, BlogModel, get_blog_model
from app.models.dates import DatesModel


class GetPageBlogsService:
    def __init__(self):
        self._repository: BlogRepository = get_blog_repository()
        self.model: Blog = get_blog_model(self._repository)
        
    def run(self, page: int, limit: int) -> Dict[str, Any]:
        self._validate()
        
        data = self.model.get_paged_blogs(page, limit)
        
        blogs = data["blogs"]
        total_count = data["total_count"]
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_previous = page > 1
        
        return {
            "status": "success",
            "blogs": blogs,
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_previous": has_previous,
            "message": "Successfully got paged blogs",
        }

    def _validate(self):
        pass

def get_get_page_blogs_service() -> GetPageBlogsService:
    return GetPageBlogsService()
