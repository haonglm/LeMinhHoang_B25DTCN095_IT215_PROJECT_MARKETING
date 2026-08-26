from datetime import datetime
from pydantic import BaseModel, Field


# Schema khi tạo bình luận mới
class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="Nội dung bình luận")


# Schema trả về dữ liệu bình luận
class CommentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True