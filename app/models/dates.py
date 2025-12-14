from typing import Optional

from pydantic import BaseModel
from datetime import date

class DatesModel(BaseModel):
    """Corresponds to the 'dates' nested object."""
    created_at: date
    published_at: Optional[date] = None
    last_update: Optional[date] = None
