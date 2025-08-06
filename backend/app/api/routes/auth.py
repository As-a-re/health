from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.core.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    get_current_user
)
from app.core.config import settings
from app.core.database import create_user, get_user_by_email, User
from app.models.schemas import UserCreate, UserResponse, Token

router = APIRouter()

@router.post("/register", response_model=dict)
async def register(user: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = await get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    user_data = {
        "email": user.email,
        "hashed_password": hashed_password,
        "full_name": user.full_name,
        "preferred_language": user.preferred_language or "en"
    }
    
    new_user = await create_user(user_data)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.id}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "preferred_language": new_user.preferred_language,
            "is_active": new_user.is_active,
            "created_at": new_user.created_at.isoformat()
        }
    }

class LoginForm:
    def __init__(
        self,
        email: str = Form(...),
        password: str = Form(...),
    ):
        self.email = email
        self.password = password

@router.post("/login", response_model=dict)
async def login(form_data: LoginForm = Depends()):
    """Login user with email and password"""
    user = await get_user_by_email(form_data.email)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "preferred_language": user.preferred_language,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        }
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        preferred_language=current_user.preferred_language,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )
