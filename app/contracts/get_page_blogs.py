from typing import List, Optional

from pydantic import BaseModel, Field
from datetime import date

from app.enums.enums import BlogState
from app.models.dates import DatesModel
from app.models.blog import BlogModel


class GetPageBlogsResponse(BaseModel):
    status: str = Field(..., description="The status of the response.")
    blogs: Optional[List[BlogModel]] = Field(..., description="List of paged blogs.")

    total_count: int
    page: int
    limit: int
    total_pages: Optional[int] = None
    has_next: Optional[bool] = None
    has_previous: Optional[bool] = None

    message: str = Field(..., description="Response detailed message.")
