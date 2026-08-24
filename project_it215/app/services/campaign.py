from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends

from models import Campaign, CampaignMember, User
from schemas import CampaignCreate, CampaignUpdate, CampaignMemberCreate
from db.database import get_db

def get_campaign_or_404(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"không tìm thấy chiến dịch có id {campaign_id}"
        )
    return campaign


def create_campaign(campaign_in: CampaignCreate, user_id: int, db: Session):
    # Tạo campaign mới
    new_campaign = Campaign(
        name=campaign_in.name,
        description=campaign_in.description,
        owner_id=user_id
    )
    db.add(new_campaign)
    db.flush()  # Lấy new_campaign.id trước khi commit

    # thêm owner vào bảng campaign_members với role OWNER
    new_member = CampaignMember(
        campaign_id=new_campaign.id,
        user_id=user_id,
        role="OWNER"
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_campaign)
    return new_campaign


def get_my_campaigns(user_id: int, db: Session, keyword: Optional[str] = None):
    # Lấy các chiến dịch mà user đang là thành viên (join bảng campaign_members)
    query = (db.query(Campaign).join(CampaignMember, Campaign.id == CampaignMember.campaign_id).filter(CampaignMember.user_id == user_id))
    if keyword:
        query = query.filter(Campaign.name.ilike(f"%{keyword}%"))
    return query.all()


def update_campaign(campaign: Campaign, campaign_in: CampaignUpdate, db: Session):
    if campaign_in.name is not None:
        campaign.name = campaign_in.name
    if campaign_in.description is not None:
        campaign.description = campaign_in.description

    db.commit()
    db.refresh(campaign)
    return campaign


def delete_campaign(campaign: Campaign, db: Session):
    # Xóa toàn bộ member thuộc campaign trước rồi xóa campaign
    db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign.id).delete()
    db.delete(campaign)
    db.commit()


def get_campaign_members(campaign_id: int, db: Session):
    return db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign_id).all()


def add_campaign_member(campaign_id: int, member_in: CampaignMemberCreate, db: Session):
    user_exists = db.query(User).filter(User.id == member_in.user_id).first()
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng được thêm không tồn tại trên hệ thống"
        )

    # Kiểm tra đã là thành viên trong chiến dịch chưa
    existed_member = db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign_id,CampaignMember.user_id == member_in.user_id).first()
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
    return new_member


def remove_campaign_member(campaign: Campaign, user_id_to_remove: int, db: Session):
    # Không được xóa Owner của chiến dịch
    if campaign.owner_id == user_id_to_remove:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa OWNER ra khỏi chiến dịch"
        )

    # Kiểm tra member có tồn tại trong chiến dịch không
    member = db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign.id,CampaignMember.user_id == user_id_to_remove).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thành viên không thuộc chiến dịch này"
        )

    db.delete(member)
    db.commit()