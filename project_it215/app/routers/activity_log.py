from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.activity_log import ActivityLogResponse
from dependencies.campaign import check_campaign_member
from services import activity_log as log_service

router = APIRouter(tags=["Activity Logs"])


# Xem lịch sử hoạt động của chiến dịch (Chỉ thành viên trong chiến dịch)
@router.get(
    "/campaigns/{campaign_id}/activity-logs",
    response_model=List[ActivityLogResponse],
    status_code=status.HTTP_200_OK,
    summary="Xem lịch sử hoạt động của chiến dịch"
)
def get_campaign_activity_logs(
    campaign_id: int,
    _member=Depends(check_campaign_member),
    db: Session = Depends(get_db)
):
    return log_service.get_logs_by_campaign(campaign_id=campaign_id, db=db)