from typing import List, Optional

from pydantic import BaseModel, Field
from datetime import date

from app.contracts.enums import BlogState
from app.contracts.dates_model import DatesModel


class RegisterBlogRequest(BaseModel):
    """
    Contract for blog registration, now expecting JSON with file paths (strings),
    not actual file objects.
    """
    title: str = Field(..., description="The title of the blog post.")
    category: str = Field(..., description="The primary category.")
    keywords: List[str] = Field(..., description="List of keywords/tags.")
    dates: DatesModel = Field(..., description="Creation, publication, and update dates.")
    
    content: str = Field(..., description="The server-side path or URL to the content markdown file.")
    references: List[str] = Field(default_factory=list, description="List of server-side paths or URLs to reference files.")
    
    state: BlogState = Field(..., description="The publication state (drafted or published).")
