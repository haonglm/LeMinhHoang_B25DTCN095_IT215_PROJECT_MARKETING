from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field

# Schema khi TẠO MỚI task (KHÔNG có assignee_id)
class CampaignTaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[Literal["TODO", "IN_PROGRESS", "DONE"]] = "TODO"
    priority: Optional[Literal["LOW", "MEDIUM", "HIGH"]] = "MEDIUM"
    due_date: Optional[datetime] = None


# Schema khi CẬP NHẬT task (Chứa tất cả các trường có thể sửa)
class CampaignTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[Literal["TODO", "IN_PROGRESS", "DONE"]] = None
    priority: Optional[Literal["LOW", "MEDIUM", "HIGH"]] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = Field(None, gt=0)


# Schema TRẢ VỀ kết quả 
class CampaignTaskResponse(BaseModel):
    id: int
    campaign_id: int
    title: str
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    status: str
    priority: str
    due_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True