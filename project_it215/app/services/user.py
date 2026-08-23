from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import User


def get_user_by_email(email: str, db: Session):
    return db.query(User).filter(User.email == email).first()


def search_users(db: Session, keyword: Optional[str] = None, is_active: Optional[bool] = None):
    query = db.query(User)

    # Tìm kiếm theo tên hoặc email nếu có truyền keyword
    if keyword:
        search_pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                User.full_name.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        )

    # Lọc theo trạng thái hoạt động
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    return query.all()