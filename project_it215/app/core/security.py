import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def handle_hash_pass(plain_pass: str):
    byte_pass = plain_pass.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(byte_pass, salt)

def verify_pass(plain_pass: str, hash_pass: str):
    return bcrypt.checkpw(plain_pass.encode("utf-8"), hash_pass.encode("utf-8"))

def handle_access_token(user_name: str, email:str, role: str):
    expire_time = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": email,
        "user_name": user_name,
        "role": role,
        "exp": expire_time
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])