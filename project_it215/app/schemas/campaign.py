from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field

#schema chiến dịch
class CampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=1000)

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=1000)

class CampaignResponse(CampaignBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# schema cho thành viên chiến dịch
class CampaignMemberBase(BaseModel):
    user_id: int = Field(..., gt=0)
    role: Optional[Literal["OWNER", "MEMBER"]] = "MEMBER"

class CampaignMemberCreate(CampaignMemberBase):
    pass

class CampaignMemberUpdate(BaseModel):
    role: Literal["OWNER", "MEMBER"]

class CampaignMemberResponse(CampaignMemberBase):
    campaign_id: int
    joined_at: datetime

    class Config:
        from_attributes = True