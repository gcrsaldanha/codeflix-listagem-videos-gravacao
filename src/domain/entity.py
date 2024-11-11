from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Entity(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = ConfigDict(extra="forbid", validate_assignment=True)
