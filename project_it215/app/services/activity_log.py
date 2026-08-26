from sqlalchemy.orm import Session
from models import ActivityLog


def log_action(campaign_id: int, user_id: int, action: str, db: Session):
    log_entry = ActivityLog(
        campaign_id=campaign_id,
        user_id=user_id,
        action=action
    )
    db.add(log_entry)
    db.commit()
    return log_entry


def get_logs_by_campaign(campaign_id: int, db: Session):
    return (db.query(ActivityLog).filter(ActivityLog.campaign_id == campaign_id).order_by(ActivityLog.created_at.desc()).all())