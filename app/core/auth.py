from passlib.context import CryptContext
from itsdangerous import URLSafeSerializer
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import User

SECRET_KEY = "hospital_super_secret_key_change_in_production"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer = URLSafeSerializer(SECRET_KEY)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_token = request.cookies.get("session_token")
    if not user_token:
        return None
    try:
        user_id = serializer.loads(user_token)
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except Exception:
        return None

def login_required(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    return user