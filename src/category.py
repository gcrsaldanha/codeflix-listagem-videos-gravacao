from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Category(BaseModel):
    id: UUID
    name: str
    description: str = ""
    created_at: datetime
    updated_at: datetime
    is_active: bool
