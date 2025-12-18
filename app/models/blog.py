from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import Depends

from app.models.abstract import AbstractModel

from app.enums.enums import BlogState
from app.models.dates import DatesModel
from app.repositories.blog import BlogRepository, get_blog_repository
from app.utils.slugify import slugify


class Blog(AbstractModel[BlogRepository]):
    class Schema(BaseModel):
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


    def find_by_permalink(self, year: str, month: str, day: str, slug: str) -> Optional[Schema]:
        data = self.repository.get_by_permalink(year, month, day, slug)
        return self.Schema(**data) if data else None

    def save(self, blog_data: Schema) -> None:
        self.repository.add(blog_data.model_dump())

    def update(self, blog_id: str, blog_data: Schema) -> None:
        self.repository.update(blog_id, blog_data.model_dump())

    def find_by_id(self, blog_id: str) -> Optional[Schema]:
        data = self.repository.get_by_id(blog_id)
        return self.Schema(**data) if data else None

    def get_page(self, page: int, limit: int, state: Optional[BlogState] = None) -> Dict[str, Any]:
        repo_data = self.repository.get_page(page, limit, state=state)
        
        return {
            "blogs": [self.Schema(**blog) for blog in repo_data.get("blogs")],
            "total_count": repo_data.get("total_count")
        }

    def get_all(self) -> List[Schema]:
        data = self.repository.get_all()
        return [self.Schema(**blog) for blog in data]


def get_blog_model(repository: BlogRepository = Depends(get_blog_repository)) -> Blog:
    return Blog(repository)
