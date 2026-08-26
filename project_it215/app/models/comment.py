from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from db import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("campaign_tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    task = relationship("CampaignTask")
    user = relationship("User")