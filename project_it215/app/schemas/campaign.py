from datetime import datetime
from typing import Optional
from pydantic import BaseModel

#schema chiến dịch
class CampaignBase(BaseModel):
    name: str 
    description: Optional[str] = None

class CampaignCreate(CampaignBase):
    pass

class campaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class CampaignResponse(CampaignBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# schema cho thành viên chiến dịch
class CampaignMemberBase(BaseModel):
    user_id: int
    role: Optional[str] = "MEMBER"

class CampaignMemberCreate(CampaignMemberBase):
    pass

class CampaignMemberUpdate(BaseModel):
    role: str

class CampaignMemberResponse(CampaignMemberBase):
    campaign_id: int
    joined_at: datetime

    class Config:
        from_attributes = True