from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from models import Campaign, CampaignMember, User
from .auth import get_current_user
from services import get_campaign_or_404



def check_campaign_member(campaign_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_campaign_or_404(campaign_id,db)

    member = db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign_id, CampaignMember.user_id == current_user.id).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="bạn không phải thành viên của chiến dịch này"
        )

    return member

def check_campaign_owner(campaign_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    campaign = get_campaign_or_404(campaign_id,db)

    if campaign.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="chỉ người tạo chiến dịch mới có quyền thực hiện thao tác"
        )

    return campaign