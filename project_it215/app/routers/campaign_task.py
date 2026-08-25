from typing import List, Optional, Literal
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from db.database import get_db
from models import CampaignTask
from schemas import CampaignTaskCreate, CampaignTaskUpdate, CampaignTaskResponse
from dependencies.campaign import check_campaign_member
from dependencies.campaign_task import check_task_member_access, check_task_modify_permission, check_task_delete_permission

from services import campaign_task as task_service

router = APIRouter(tags=["Campaign Tasks"])


# Tạo đầu việc
@router.post("/campaigns/{campaign_id}/campaign-tasks", response_model=CampaignTaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    campaign_id: int,
    task_in: CampaignTaskCreate,
    _member=Depends(check_campaign_member),
    db: Session = Depends(get_db)
):
    return task_service.create_task(campaign_id, task_in, db)


# Danh sách đầu việc
@router.get("/campaigns/{campaign_id}/campaign-tasks", response_model=List[CampaignTaskResponse], status_code=status.HTTP_200_OK)
def get_campaign_tasks(
    campaign_id: int,
    title: Optional[str] = Query(None, description="Tìm theo tiêu đề"),
    status_filter: Optional[Literal["TODO", "IN_PROGRESS", "DONE"]] = Query(None, alias="status"),
    priority: Optional[Literal["LOW", "MEDIUM", "HIGH"]] = Query(None),
    assignee_id: Optional[int] = Query(None),
    sort_by: Optional[Literal["created_at", "due_date"]] = Query("created_at"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    _member=Depends(check_campaign_member),
    db: Session = Depends(get_db)
):
    return task_service.get_campaign_tasks(
        campaign_id=campaign_id,
        db=db,
        title=title,
        task_status=status_filter,
        priority=priority,
        assignee_id=assignee_id,
        sort_by=sort_by,
        page=page,
        size=size
    )


# Chi tiết đầu việc
@router.get("/campaign-tasks/{task_id}", response_model=CampaignTaskResponse, status_code=status.HTTP_200_OK)
def get_task_detail(task: CampaignTask = Depends(check_task_member_access)):
    return task


# Cập nhật đầu việc
@router.patch("/campaign-tasks/{task_id}", response_model=CampaignTaskResponse, status_code=status.HTTP_200_OK)
def update_task(task_in: CampaignTaskUpdate, task: CampaignTask = Depends(check_task_modify_permission), db: Session = Depends(get_db)):
    return task_service.update_task(task, task_in, db)


# Xóa đầu việc
@router.delete("/campaign-tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task( task: CampaignTask = Depends(check_task_delete_permission), db: Session = Depends(get_db)):
    task_service.delete_task(task, db)
    return None