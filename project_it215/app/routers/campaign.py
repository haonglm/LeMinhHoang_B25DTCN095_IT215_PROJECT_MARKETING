from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from db.database import get_db
from models import User, Campaign
from schemas import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignMemberCreate, CampaignMemberResponse


from dependencies.auth import get_current_user
from dependencies.campaign import check_campaign_member, check_campaign_owner
from services import campaign as campaign_service

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


# Tạo chiến dịch
@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(
    campaign_in: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return campaign_service.create_campaign(campaign_in, current_user.id, db)


# Danh sách chiến dịch kèm tìm kiếm
@router.get("", response_model=List[CampaignResponse], status_code=status.HTTP_200_OK)
def get_my_campaigns(
    name: Optional[str] = Query(None, description="Tìm theo tên chiến dịch"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return campaign_service.get_my_campaigns(current_user.id, db, keyword=name)


# Chi tiết chiến dịch (Member)
@router.get("/{campaign_id}", response_model=CampaignResponse, status_code=status.HTTP_200_OK)
def get_campaign_detail(
    campaign_id: int,
    _member=Depends(check_campaign_member),
    db: Session = Depends(get_db)
):
    return campaign_service.get_campaign_or_404(campaign_id, db)


# Cập nhật chiến dịch (Owner)
@router.patch("/{campaign_id}", response_model=CampaignResponse, status_code=status.HTTP_200_OK)
def update_campaign(
    campaign_in: CampaignUpdate,
    campaign: Campaign = Depends(check_campaign_owner),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return campaign_service.update_campaign(campaign, campaign_in, current_user.id, db)


# Xóa mềm chiến dịch (Owner)
@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(
    campaign: Campaign = Depends(check_campaign_owner),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    campaign_service.delete_campaign(campaign, current_user.id, db)
    return None


# Thêm thành viên vào chiến dịch (Owner)
@router.post("/{campaign_id}/members", response_model=CampaignMemberResponse, status_code=status.HTTP_201_CREATED)
def add_member(
    campaign_id: int,
    member_in: CampaignMemberCreate,
    _owner=Depends(check_campaign_owner),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return campaign_service.add_campaign_member(campaign_id, member_in, current_user.id, db)


# Danh sách thành viên (Member)
@router.get("/{campaign_id}/members", response_model=List[CampaignMemberResponse], status_code=status.HTTP_200_OK)
def get_members(
    campaign_id: int,
    _member=Depends(check_campaign_member),
    db: Session = Depends(get_db)
):
    return campaign_service.get_campaign_members(campaign_id, db)


# Xóa thành viên (Owner)
@router.delete("/{campaign_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    user_id: int,
    campaign: Campaign = Depends(check_campaign_owner),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    campaign_service.remove_campaign_member(campaign, user_id, current_user.id, db)
    return None