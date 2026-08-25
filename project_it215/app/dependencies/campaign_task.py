from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from models import CampaignTask, CampaignMember, Campaign, User
from dependencies.auth import get_current_user


def get_task_or_404(task_id: int, db: Session = Depends(get_db)):
    task = db.query(CampaignTask).filter(CampaignTask.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy công việc với id {task_id}"
        )
    return task


# Kiểm tra xem User có phải thành viên của Campaign chứa Task này không
def check_task_member_access(
    task: CampaignTask = Depends(get_task_or_404),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    is_member = db.query(CampaignMember).filter(
        CampaignMember.campaign_id == task.campaign_id,
        CampaignMember.user_id == current_user.id
    ).first()

    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập đầu việc này"
        )
    return task


# Chỉ OWNER chiến dịch hoặc chính Assignee của task mới được sửa
def check_task_modify_permission(
    task: CampaignTask = Depends(get_task_or_404),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    campaign = db.query(Campaign).filter(Campaign.id == task.campaign_id).first()

    is_owner = (campaign.owner_id == current_user.id)
    is_assignee = (task.assignee_id == current_user.id)

    if not (is_owner or is_assignee):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ OWNER chiến dịch hoặc người được giao việc mới có quyền cập nhật"
        )
    return task


# Chỉ OWNER chiến dịch mới được xóa
def check_task_delete_permission(
    task: CampaignTask = Depends(get_task_or_404),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CampaignTask:
    campaign = db.query(Campaign).filter(Campaign.id == task.campaign_id).first()
    
    if campaign.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ OWNER chiến dịch mới có quyền xóa đầu việc"
        )
    return task