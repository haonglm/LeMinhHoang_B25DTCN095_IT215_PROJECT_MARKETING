from typing import List
from sqlalchemy.orm import Session
from models import Comment, CampaignTask
from schemas import CommentCreate
from services import activity_log as log_service


def create_comment(task: CampaignTask, user_id: int, comment_in: CommentCreate, db: Session) -> Comment:
    new_comment = Comment(
        task_id=task.id,
        user_id=user_id,
        content=comment_in.content
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    # 9. LOG TẠO COMMENT
    log_service.log_action(task.campaign_id, user_id, "CREATE_COMMENT", db)

    return new_comment


def get_comments_by_task(task_id: int, db: Session) -> List[Comment]:
    return (db.query(Comment).filter(Comment.task_id == task_id).order_by(Comment.created_at.asc()).all())