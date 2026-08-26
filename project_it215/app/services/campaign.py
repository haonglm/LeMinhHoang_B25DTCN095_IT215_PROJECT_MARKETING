from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends

from models import Campaign, CampaignMember, User
from schemas import CampaignCreate, CampaignUpdate, CampaignMemberCreate
from db.database import get_db
from services import activity_log as log_service


def get_campaign_or_404(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.is_deleted == False
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"không tìm thấy chiến dịch có id {campaign_id}"
        )
    return campaign


def create_campaign(campaign_in: CampaignCreate, user_id: int, db: Session):
    new_campaign = Campaign(
        name=campaign_in.name,
        description=campaign_in.description,
        owner_id=user_id
    )
    db.add(new_campaign)
    db.flush()

    new_member = CampaignMember(
        campaign_id=new_campaign.id,
        user_id=user_id,
        role="OWNER"
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_campaign)

    # 1. LOG TẠO CHIẾN DỊCH
    log_service.log_action(new_campaign.id, user_id, "CREATE_CAMPAIGN", db)

    return new_campaign


def get_my_campaigns(user_id: int, db: Session, keyword: Optional[str] = None):
    query = (
        db.query(Campaign)
        .join(CampaignMember, Campaign.id == CampaignMember.campaign_id)
        .filter(
            CampaignMember.user_id == user_id,
            Campaign.is_deleted == False
        )
    )
    if keyword:
        query = query.filter(Campaign.name.ilike(f"%{keyword}%"))
    return query.all()


def update_campaign(campaign: Campaign, campaign_in: CampaignUpdate, current_user_id: int, db: Session):
    if campaign_in.name is not None:
        campaign.name = campaign_in.name
    if campaign_in.description is not None:
        campaign.description = campaign_in.description

    db.commit()
    db.refresh(campaign)

    # 2. LOG CẬP NHẬT CHIẾN DỊCH
    log_service.log_action(campaign.id, current_user_id, "UPDATE_CAMPAIGN", db)

    return campaign


def delete_campaign(campaign: Campaign, current_user_id: int, db: Session):
    campaign.is_deleted = True
    campaign.deleted_at = datetime.now(timezone.utc)
    db.commit()

    # 3. LOG XÓA MỀM CHIẾN DỊCH
    log_service.log_action(campaign.id, current_user_id, "DELETE_CAMPAIGN", db)


def get_campaign_members(campaign_id: int, db: Session):
    return db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign_id).all()


def add_campaign_member(campaign_id: int, member_in: CampaignMemberCreate, current_user_id: int, db: Session):
    user_exists = db.query(User).filter(User.id == member_in.user_id).first()
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng được thêm không tồn tại trên hệ thống"
        )

    existed_member = db.query(CampaignMember).filter(
        CampaignMember.campaign_id == campaign_id,
        CampaignMember.user_id == member_in.user_id
    ).first()
    if existed_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Người dùng này đã là thành viên của chiến dịch"
        )

    new_member = CampaignMember(
        campaign_id=campaign_id,
        user_id=member_in.user_id,
        role=member_in.role or "MEMBER"
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    # 4. LOG THÊM MEMBER
    log_service.log_action(campaign_id, current_user_id, "ADD_MEMBER", db)

    return new_member


def remove_campaign_member(campaign: Campaign, user_id_to_remove: int, current_user_id: int, db: Session):
    if campaign.owner_id == user_id_to_remove:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa OWNER ra khỏi chiến dịch"
        )

    member = db.query(CampaignMember).filter(
        CampaignMember.campaign_id == campaign.id,
        CampaignMember.user_id == user_id_to_remove
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thành viên không thuộc chiến dịch này"
        )

    db.delete(member)
    db.commit()

    # 5. LOG XÓA MEMBER
    log_service.log_action(campaign.id, current_user_id, "REMOVE_MEMBER", db)