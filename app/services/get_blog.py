from typing import Any, Dict
import os
from datetime import date

from app.repositories.blogs import BlogRepository, get_blog_repository
from app.models.blog import Blog, BlogModel, get_blog_model
from app.models.dates import DatesModel
from app.utils.slugify import slugify


class GetBlogService:
    def __init__(self):
        self._repository: BlogRepository = get_blog_repository()
        self.model: Blog = get_blog_model(self._repository)
        
    def run(self, year: int, month: int, day: int, title: str) -> Dict[str, Any]:
        self._validate()

        full_permalink = f"{year}/{month}/{day}/{slugify(title)}"
        blog = self.model.find_by_permalink(full_permalink)

        return {
            "status": "success",
            "blog": blog,
            "message": f"Successfully found blog.",
        }

    def _validate(self):
        pass

def get_get_blog_service() -> GetBlogService:
    return GetBlogService()
