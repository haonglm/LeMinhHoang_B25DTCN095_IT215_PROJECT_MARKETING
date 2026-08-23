from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from db.database import get_db
from models import User
from schemas import UserResponse
from dependencies import get_current_user, RoleCheck
from services import user as user_service

# quyền Admin
ALLOWED_ADMIN = RoleCheck(allowed_roles=["ADMIN"])

router = APIRouter(prefix="/users", tags=["Users"])

# Profile người dùng hiện tại không lộ mk 
@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK, summary="Lấy thông tin tài khoản hiện tại")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# Danh sách người dùng dành cho Admin
@router.get("",response_model=List[UserResponse],status_code=status.HTTP_200_OK, summary="Lấy danh sách người dùng (Chỉ Admin)")
def get_all_users(keyword: Optional[str] = Query(None, description="Tìm kiếm theo tên hoặc email"), is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái hoạt động"), current_admin: User = Depends(ALLOWED_ADMIN), db: Session = Depends(get_db)):
    return user_service.search_users(db=db, keyword=keyword, is_active=is_active)