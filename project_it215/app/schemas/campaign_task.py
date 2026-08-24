from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field

#schema cơ bản 
class CampaignTaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=1000)
    assignee_id: Optional[int] = ()
    status: Optional[Literal["TODO", "IN_PROGRESS", "DONE"]] = "TODO" #todo/in_progress/done
    priority: Optional[Literal["LOW", "MEDIUM", "HIGH"]] = "MEDIUM" #low/medium/high

# khi tạo mới task 
class CampaignTaskCreate(CampaignTaskBase):
    pass

#khi cập nhật task
class CampaignTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=1000)
    assignee_id: Optional[int] = Field(None, gt=0)
    status: Optional[Literal["TODO", "IN_PROGRESS", "DONE"]] = None
    priority: Optional[Literal["LOW", "MEDIUM", "HIGH"]] = None
    duedate: Optional[datetime] = None

# dữ liệu trả về kết quả việc
class CampaignTaskResponse(CampaignTaskBase):
    id: int
    campaign_id: int
    created_at: datetime

    class Config:
        from_attributes = True