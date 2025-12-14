from typing import Any, Dict
import os
from datetime import date

from app.repositories.blogs import BlogRepository, get_blog_repository
from app.models.blog import Blog, BlogModel, get_blog_model
from app.models.dates import DatesModel


class GetBlogService:
    def __init__(self):
        self._repository: BlogRepository = get_blog_repository()
        self.model: Blog = get_blog_model(self._repository)
        
    def run(self, blog_id: int) -> Dict[str, Any]:
        self._validate()
        
        blog = self.model.find_by_id(blog_id)
        return {
            "status": "success",
            "blog": blog,
            "message": f"Successfully found blog with ID ({blog_id})",
        }

    def _validate(self):
        pass

def get_get_blog_service() -> GetBlogService:
    return GetBlogService()
