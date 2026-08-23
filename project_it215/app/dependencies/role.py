from typing import List
from fastapi import Depends, HTTPException, status
from models import User
from .auth import get_current_user


class RoleCheck:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = [r.upper() for r in allowed_roles]

    def __call__(self, current_user: User = Depends(get_current_user)):
        # Kiểm tra role của user có nằm trong danh sách cho phép không
        if current_user.role.upper() not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập tài nguyên này"
            )
        return current_user