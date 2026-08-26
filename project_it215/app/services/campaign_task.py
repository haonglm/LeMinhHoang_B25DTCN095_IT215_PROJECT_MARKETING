from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import CampaignTask, CampaignMember, Campaign
from schemas import CampaignTaskCreate, CampaignTaskUpdate
from services import activity_log as log_service


def create_task(campaign_id: int, task_in: CampaignTaskCreate, user_id: int, db: Session) -> CampaignTask:
    new_task = CampaignTask(
        campaign_id=campaign_id,
        title=task_in.title,
        description=task_in.description,
        assignee_id=None,
        status=task_in.status or "TODO",
        priority=task_in.priority or "MEDIUM",
        due_date=task_in.due_date
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # 6. LOG TẠO TASK
    log_service.log_action(campaign_id, user_id, "CREATE_TASK", db)

    return new_task


def get_campaign_tasks(
    campaign_id: int,
    db: Session,
    title: Optional[str] = None,
    task_status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    sort_by: Optional[str] = "created_at",
    page: int = 1,
    size: int = 10
) -> List[CampaignTask]:
    query = db.query(CampaignTask).filter(CampaignTask.campaign_id == campaign_id)

    if title:
        query = query.filter(CampaignTask.title.ilike(f"%{title}%"))
    if task_status:
        query = query.filter(CampaignTask.status == task_status)
    if priority:
        query = query.filter(CampaignTask.priority == priority)
    if assignee_id:
        query = query.filter(CampaignTask.assignee_id == assignee_id)

    if sort_by == "due_date":
        query = query.order_by(CampaignTask.due_date.asc())
    else:
        query = query.order_by(CampaignTask.created_at.desc())

    offset = (page - 1) * size
    return query.offset(offset).limit(size).all()


def update_task(task: CampaignTask, task_in: CampaignTaskUpdate, user_id: int, db: Session) -> CampaignTask:
    update_data = task_in.model_dump(exclude_unset=True)

    campaign = db.query(Campaign).filter(Campaign.id == task.campaign_id).first()
    is_owner = (campaign.owner_id == user_id) if campaign else False

    if not is_owner:
        if "assignee_id" in update_data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ OWNER mới có quyền phân công (gán assignee_id)"
            )
        if "priority" in update_data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ OWNER mới có quyền thay đổi độ ưu tiên (priority)"
            )

    if is_owner and "assignee_id" in update_data and update_data["assignee_id"] is not None:
        member = db.query(CampaignMember).filter(
            CampaignMember.campaign_id == task.campaign_id,
            CampaignMember.user_id == update_data["assignee_id"]
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người được giao việc mới không thuộc chiến dịch này"
            )

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    # 7. LOG SỬA TASK
    log_service.log_action(task.campaign_id, user_id, "UPDATE_TASK", db)

    return task


def delete_task(task: CampaignTask, user_id: int, db: Session):
    campaign_id = task.campaign_id
    db.delete(task)
    db.commit()

    # 8. LOG XÓA TASK
    log_service.log_action(campaign_id, user_id, "DELETE_TASK", db)