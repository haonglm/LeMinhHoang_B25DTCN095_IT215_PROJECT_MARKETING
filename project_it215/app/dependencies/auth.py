import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from db.database import get_db
from core.config import SECRET_KEY, ALGORITHM
from services.user import get_user_by_email

# Khởi tạo Bearer schema để hiện nút Authorize trên Swagger UI
security_scheme = HTTPBearer()

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security_scheme), db: Session = Depends(get_db)):
    # lấy token
    # Nếu client không gửi Header 'Authorization: Bearer <token>' thì creds sẽ là None
    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Vui lòng cung cấp Access Token"
        )

    # Lấy ra chuỗi token thực sự : bỏ chữ Bearer
    token = creds.credentials

    # giải mã token
    try:
        # Dùng SECRET_KEY để mở khóa payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Lấy email từ sub đã lưu lúc login
        user_email = payload.get("sub")
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ"
            )
    except jwt.ExpiredSignatureError:
        # Bắt lỗi nếu thời gian exp trong token đã quá hạn
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token đã hết hạn"
        )
    except jwt.PyJWTError:
        # Bắt lỗi nếu token bị sửa đổi, sai SECRET_KEY hoặc sai định dạng
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ"
        )

    # Lấy user từ DB theo email vừa giải mã được
    user_db = get_user_by_email(user_email, db)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại"
        )

    # Nếu admin đã set is_active = False, chặn không cho dùng API
    if not user_db.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khóa"
        )

    return user_db