from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)

    owner = relationship("User", back_populates="owned_campaigns")

    members = relationship("CampaignMember", back_populates="campaign")

    tasks = relationship("CampaignTask", back_populates="campaign")

class CampaignMember(Base):
    __tablename__ = "campaign_members"

    # khóa chính phức hợp để cặp campaign_id và user_id là duy nhất
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    role = Column(String(20), default="MEMBER", nullable=False)
    joined_at = Column(DateTime, nullable=False)

    campaign = relationship("Campaign", back_populates="members")

    user = relationship("User", back_populates="campaign_memberships")

