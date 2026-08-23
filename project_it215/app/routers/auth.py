from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from db.database import get_db
from schemas import UserCreate, UserResponse, Token
from services import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    return register_user(user_in, db)

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(login_in: UserCreate, db: Session = Depends(get_db)):
    login_data = {
        "email": login_in.email,
        "password": login_in.password
    }

    return login_user(login_data, db)