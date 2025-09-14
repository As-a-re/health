from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
from jose import JWTError, jwt

from models.user import (
    UserCreate, UserInDB, Token, TokenData,
    verify_password, get_password_hash, create_access_token
)
from config import get_settings

settings = get_settings()
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# MongoDB client
client = MongoClient(settings.MONGODB_URL)
db = client.get_database()
users_collection = db["users"]

# Create indexes
users_collection.create_index("email", unique=True)

async def get_user(email: str) -> UserInDB | None:
    user_data = users_collection.find_one({"email": email})
    if user_data:
        user_data["_id"] = str(user_data["_id"])  # Convert ObjectId to string
        return UserInDB(**user_data)
    return None

async def authenticate_user(email: str, password: str) -> UserInDB | bool:
    print(f"Attempting to authenticate user: {email}")
    user = await get_user(email)
    if not user:
        print(f"User {email} not found")
        return False
    
    print(f"User found: {user}")
    print(f"Stored hash: {user.hashed_password}")
    print(f"Verifying password for {email}")
    
    if not verify_password(password, user.hashed_password):
        print("Password verification failed")
        return False
        
    print("Authentication successful")
    return user

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/signup", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    # Check if user already exists
    if await get_user(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.dict()
    del user_dict["password"]
    user_dict["hashed_password"] = hashed_password
    
    # Insert into database
    result = users_collection.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)
    
    return UserInDB(**user_dict)

@router.post("/login", response_model=dict, status_code=status.HTTP_200_OK)
async def login_for_access_token(login_data: LoginRequest):
    user = await authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    # Convert user to dict and handle ObjectId serialization
    user_dict = user.dict(by_alias=True)
    if '_id' in user_dict:
        user_dict['id'] = str(user_dict['_id'])
        del user_dict['_id']
    
    # Remove sensitive data
    user_dict.pop('hashed_password', None)
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": user_dict
    }

@router.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint is working!"}

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = await get_user(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

@router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }
