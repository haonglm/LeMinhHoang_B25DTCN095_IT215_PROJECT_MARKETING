from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.database import get_db
from models import CampaignTask, User
from schemas import CommentCreate, CommentResponse
from dependencies.auth import get_current_user
from dependencies.campaign_task import check_task_member_access
from services import comment as comment_service

router = APIRouter(tags=["Comments"])


# Tạo comment cho task (Chỉ thành viên trong chiến dịch mới được comment)
@router.post(
    "/campaign-tasks/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm bình luận cho công việc"
)
def create_comment(
    comment_in: CommentCreate,
    task: CampaignTask = Depends(check_task_member_access),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return comment_service.create_comment(
        task=task,
        user_id=current_user.id,
        comment_in=comment_in,
        db=db
    )


# Lấy danh sách comment của task (Chỉ thành viên trong chiến dịch mới được xem)
@router.get(
    "/campaign-tasks/{task_id}/comments",
    response_model=List[CommentResponse],
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách bình luận của công việc"
)
def get_task_comments(
    task: CampaignTask = Depends(check_task_member_access),
    db: Session = Depends(get_db)
):
    return comment_service.get_comments_by_task(task_id=task.id, db=db)