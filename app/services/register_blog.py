from typing import Any, Dict
import os
from datetime import date

from app.contracts.register_blog import RegisterBlogRequest
from app.repositories.blogs import BlogRepository, get_blog_repository
from app.models.blog import Blog, BlogModel, get_blog_model
from app.models.dates import DatesModel


class RegisterBlogService:
    def __init__(self):
        self._repository: BlogRepository = get_blog_repository()
        self.model: Blog = get_blog_model(self._repository)

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
    
    def run(self, request: RegisterBlogRequest) -> Dict[str, Any]:
        self._validate()

        file_metadata = self._extract_file_metadata(request.content_file)
        dates = DatesModel(
            created_at=date.fromtimestamp(file_metadata['created_at_ts']),
            published_at=request.published_at,
            last_update=date.fromtimestamp(file_metadata['last_update_ts']),
        )

        blog = BlogModel(
            id=file_metadata['id'],
            title=request.title,
            category=request.category,
            keywords=request.keywords,
            dates=dates,
            content_file=request.content_file,
            references=request.references,
            state=request.state.value,
        )
        
        self.model.save(blog)
        return {
            "status": "success",
            "id": blog.id,
            "message": f"Blog with ID ({blog.id}) was registered successfully",
        }

    def _validate(self):
        pass

def get_register_blog_service() -> RegisterBlogService:
    return RegisterBlogService()
