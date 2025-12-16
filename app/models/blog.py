from typing import List, Dict, Any, Optional
from datetime import date
from pydantic import BaseModel, Field
from fastapi import Depends

from app.enums.enums import BlogState
from app.models.dates import DatesModel
from app.repositories.blogs import BlogRepository, get_blog_repository

from app.utils.slugify import slugify

# TODO: combine both classes (attributes & functions), and create another abstracted
# class for Blog(...) to inherit, such that the abstraction initializes the repository
# connection and Blog() can `self.repository` that while implementing the inherited functions
class BlogModel(BaseModel):
    id: str
    title: str
    category: str
    keywords: List[str]
    dates: DatesModel
    content_file: str
    references: List[str]
    state: BlogState

    @property
    def permalink_key(self) -> str:
        publish_date = self.dates.published_at or self.dates.created_at
        
        year = publish_date.strftime("%Y")
        month = publish_date.strftime("%m")
        day = publish_date.strftime("%d")
        slug = slugify(self.title)

        return f"{year}/{month}/{day}/{slug}"


class Blog:
    def __init__(self, repository: BlogRepository):
        self.repository = repository

    def find_by_permalink(self, permalink: str) -> Optional[BlogModel]:
        data = self.repository.find_by_permalink(permalink)
        if data:
            return BlogModel(**data)
        return None
        
    def save(self, blog_data: BlogModel) -> None:
        self.repository.add_blog(blog_data.model_dump())

    def find_by_id(self, blog_id: str) -> Optional[BlogModel]:
        data = self.repository.find_by_id(blog_id)
        if data:
            return BlogModel(**data) 
        return None

    def get_paged_blogs(self, page: int, limit: int) -> Dict[str, Any]:
        repo_data = self.repository.read_paged_blogs(page, limit)
        blogs = [BlogModel(**blog) for blog in repo_data.get("blogs")]
        
        blogs.sort(key=lambda b: b.dates.published_at or b.dates.created_at, reverse=True)

        return {
            "blogs": blogs,
            "total_count": repo_data.get("total_count")
        }
    
    def get_all(self) -> List[BlogModel]:
        blogs = self.repository.get_all()
        return [BlogModel(**blog) for blog in blogs]


def get_blog_model(blog_repository: BlogRepository = Depends(get_blog_repository)) -> Blog:
    return Blog(blog_repository)
