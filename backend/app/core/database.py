from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid
from typing import Optional, Dict, Any
import asyncio

from app.core.config import settings

# MongoDB setup
mongodb_client = None
mongodb_db = None

class User:
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id', str(uuid.uuid4()))
        self.email = kwargs.get('email')
        self.hashed_password = kwargs.get('hashed_password')
        self.full_name = kwargs.get('full_name')
        self.preferred_language = kwargs.get('preferred_language', 'en')
        self.is_active = kwargs.get('is_active', False)  # Default to False until email is verified
        self.email_verified = kwargs.get('email_verified', False)
        self.email_verification_token = kwargs.get('email_verification_token')
        self.email_verification_sent_at = kwargs.get('email_verification_sent_at')
        self.password_reset_token = kwargs.get('password_reset_token')
        self.password_reset_sent_at = kwargs.get('password_reset_sent_at')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())

class HealthQuery:
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id', str(uuid.uuid4()))
        self.user_id = kwargs.get('user_id')
        self.query_text = kwargs.get('query_text')
        self.query_language = kwargs.get('query_language', 'en')
        self.response_text = kwargs.get('response_text')
        self.response_language = kwargs.get('response_language', 'en')
        self.confidence_score = kwargs.get('confidence_score')
        self.model_used = kwargs.get('model_used')
        self.created_at = kwargs.get('created_at', datetime.utcnow())

async def init_db():
    """Initialize MongoDB database"""
    global mongodb_client, mongodb_db
    
    try:
        # Initialize MongoDB
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb_db = mongodb_client.akan_health_db
        
        # Test connection
        await mongodb_client.admin.command('ping')
        
        # Create indexes
        await mongodb_db.users.create_index("email", unique=True)
        await mongodb_db.health_queries.create_index("user_id")
        await mongodb_db.health_queries.create_index("created_at")
        await mongodb_db.query_logs.create_index("timestamp")
        await mongodb_db.error_logs.create_index("timestamp")
        
        print("✅ MongoDB initialized successfully")
        
    except Exception as e:
        print(f"❌ MongoDB initialization failed: {e}")
        raise

async def get_mongodb():
    """Get MongoDB database"""
    return mongodb_db

async def close_db_connections():
    """Close database connections"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()

# User operations
async def create_user(user_data: dict) -> User:
    """Create a new user"""
    user_doc = {
        "_id": str(uuid.uuid4()),
        "email": user_data["email"],
        "hashed_password": user_data["hashed_password"],
        "full_name": user_data.get("full_name"),
        "preferred_language": user_data.get("preferred_language", "en"),
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await mongodb_db.users.insert_one(user_doc)
    return User(**user_doc)

async def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email"""
    user_doc = await mongodb_db.users.find_one({"email": email})
    return User(**user_doc) if user_doc else None

async def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID"""
    user_doc = await mongodb_db.users.find_one({"_id": user_id})
    return User(**user_doc) if user_doc else None

# Health query operations
async def create_health_query(query_data: dict) -> HealthQuery:
    """Create a new health query"""
    query_doc = {
        "_id": str(uuid.uuid4()),
        "user_id": query_data.get("user_id"),
        "query_text": query_data["query_text"],
        "query_language": query_data.get("query_language", "en"),
        "response_text": query_data["response_text"],
        "response_language": query_data.get("response_language", "en"),
        "confidence_score": query_data.get("confidence_score"),
        "model_used": query_data.get("model_used"),
        "created_at": datetime.utcnow()
    }
    
    await mongodb_db.health_queries.insert_one(query_doc)
    return HealthQuery(**query_doc)

async def get_user_health_queries(user_id: str, skip: int = 0, limit: int = 20):
    """Get user's health queries with pagination"""
    cursor = mongodb_db.health_queries.find(
        {"user_id": user_id}
    ).sort("created_at", -1).skip(skip).limit(limit)
    
    queries = []
    async for doc in cursor:
        queries.append(HealthQuery(**doc))
    
    total_count = await mongodb_db.health_queries.count_documents({"user_id": user_id})
    
    return queries, total_count
