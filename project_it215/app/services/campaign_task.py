from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import CampaignTask, CampaignMember
from schemas import CampaignTaskCreate, CampaignTaskUpdate


def create_task(campaign_id: int, task_in: CampaignTaskCreate, db: Session):
    if task_in.assignee_id:
        member = db.query(CampaignMember).filter(
            CampaignMember.campaign_id == campaign_id,
            CampaignMember.user_id == task_in.assignee_id
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người được giao việc (assignee) không thuộc chiến dịch này"
            )

    new_task = CampaignTask(
        campaign_id=campaign_id,
        title=task_in.title,
        description=task_in.description,
        assignee_id=task_in.assignee_id,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.due_date
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
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
):
    query = db.query(CampaignTask).filter(CampaignTask.campaign_id == campaign_id)

    # tìm kiếm và lọc
    if title:
        query = query.filter(CampaignTask.title.ilike(f"%{title}%"))
    if task_status:
        query = query.filter(CampaignTask.status == task_status)
    if priority:
        query = query.filter(CampaignTask.priority == priority)
    if assignee_id:
        query = query.filter(CampaignTask.assignee_id == assignee_id)

    # sort
    if sort_by == "due_date":
        query = query.order_by(CampaignTask.due_date.asc())
    else:
        query = query.order_by(CampaignTask.created_at.desc())

    # phân trang
    offset = (page - 1) * size
    return query.offset(offset).limit(size).all()


def update_task(task: CampaignTask, task_in: CampaignTaskUpdate, db: Session):
    update_data = task_in.model_dump(exclude_unset=True)

    if "assignee_id" in update_data and update_data["assignee_id"] is not None:
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
    return task


def delete_task(task: CampaignTask, db: Session):
    db.delete(task)
    db.commit()