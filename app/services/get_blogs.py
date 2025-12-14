from typing import Any, Dict
import os
from datetime import date

from app.repositories.blogs import BlogRepository, get_blog_repository
from app.models.blog import Blog, BlogModel, get_blog_model
from app.models.dates import DatesModel


class GetBlogsService:
    def __init__(self):
        self._repository: BlogRepository = get_blog_repository()
        self.model: Blog = get_blog_model(self._repository)
        
    def run(self) -> Dict[str, Any]:
        self._validate()
        
        blogs = self.model.get_all()
        return {
            "status": "success",
            "blogs": blogs,
            "message": "Successfully got all blogs",
        }

    def _validate(self):
        pass

def get_get_blogs_service() -> GetBlogsService:
    return GetBlogsService()
