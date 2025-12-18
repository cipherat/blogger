from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DatesModel(BaseModel):
    created_at: datetime
    published_at: Optional[datetime] = None
    last_update: datetime
