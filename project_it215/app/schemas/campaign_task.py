from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

#schema cơ bản 
class CampaignTaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    status: Optional[str] = "TODO" #todo/in_progress/done
    priority: Optional[str] = "MEDIUM" #low/medium/high

# khi tạo mới task 
class CampaignTaskCreate(CampaignTaskBase):
    pass

#khi cập nhật task
class CampaignTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    duedate: Optional[datetime] = None

# dữ liệu trả về kết quả việc
class CampaignTaskResponse(CampaignTaskBase):
    id: int
    campaign_id: int
    created_at: datetime

    class Config:
        from_attributes = True