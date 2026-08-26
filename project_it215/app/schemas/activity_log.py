from datetime import datetime
from pydantic import BaseModel


class ActivityLogResponse(BaseModel):
    id: int
    campaign_id: int
    user_id: int
    action: str
    created_at: datetime

    class Config:
        from_attributes = True