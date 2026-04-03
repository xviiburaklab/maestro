from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from common.schemas import UserCreate, UserResponse, Token
from common.auth_utils import create_access_token, create_refresh_token, verify_password, get_password_hash, decode_token
from common.exceptions import AuthException, ConflictException
from .models import User, get_db
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise ConflictException("Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise AuthException("Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return {"access_token": access_token, "refresh_token": refresh_token}

@router.post("/refresh", response_model=Token)
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise AuthException("Invalid token type")
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise AuthException("User not found")
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    new_refresh_token = create_refresh_token(data={"sub": user.username})
    
    return {"access_token": access_token, "refresh_token": new_refresh_token}
