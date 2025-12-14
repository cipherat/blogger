from typing import List, Optional

from pydantic import BaseModel, Field
from datetime import date

from app.enums.enums import BlogState
from app.models.dates import DatesModel
from app.models.blog import BlogModel


class GetBlogsResponse(BaseModel):
    status: str = Field(..., description="The status of the response.")
    blogs: Optional[List[BlogModel]] = Field(..., description="List of all blogs.")
    message: str = Field(..., description="Response detailed message.")
