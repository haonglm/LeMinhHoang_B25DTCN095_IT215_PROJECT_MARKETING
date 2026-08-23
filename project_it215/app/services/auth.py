from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate
from core.security import handle_hash_pass, verify_pass, handle_access_token

def register_user(user_data: UserCreate, db: Session):
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email đã được dùng"
        )

    hashed_password = handle_hash_pass(user_data.password)

    new_user = User(
        email = user_data.email,
        full_name = user_data.full_name,
        password_hash = hashed_password,
        role = "USER",
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def login_user(login_data: dict, db: Session):
    user = db.query(User).filter(User.email == login_data.get("email")).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email hoặc mật khẩu không chính xác"
        )

    if not verify_pass(login_data.get("password"), user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email hoặc mật khẩu không chính xác"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản đang bị vô hiệu hóa"
        )

    token = handle_access_token(
        user_name=user.full_name,
        email=user.email,
        role=user.role
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }