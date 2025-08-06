from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    preferred_language: Optional[str] = "en"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    preferred_language: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    preferred_language: str
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

# Health query schemas
class HealthQueryRequest(BaseModel):
    question: str
    language: Optional[str] = "auto"
    include_translation: Optional[bool] = False

class HealthQueryResponse(BaseModel):
    response: str
    confidence: float
    language: str
    model_used: str
    query_id: Optional[str] = None
    translation: Optional[Dict[str, str]] = None
    search_results: Optional[int] = 0

class AudioQueryRequest(BaseModel):
    language: Optional[str] = "auto"
    include_translation: Optional[bool] = True

class AudioQueryResponse(BaseModel):
    transcription: str
    transcription_language: str
    response: str
    confidence: float
    language: str
    model_used: str
    query_id: Optional[str] = None

# History schemas
class HealthQueryItem(BaseModel):
    id: str
    query_text: str
    query_language: str
    response_text: str
    response_language: str
    confidence_score: Optional[str]
    model_used: Optional[str]
    created_at: str

class HealthQueryHistory(BaseModel):
    queries: List[HealthQueryItem]
    total_count: int
    page: int
    page_size: int
    total_pages: int

# Log schemas
class QueryLog(BaseModel):
    id: str
    endpoint: str
    method: str
    status_code: int
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    query_params: Optional[Dict[str, Any]] = None
    request_body: Optional[Dict[str, Any]] = None
    response_body: Optional[Dict[str, Any]] = None
    duration: float
    created_at: datetime

class LogsResponse(BaseModel):
    logs: List[QueryLog]
    total_count: int
    page: int
    page_size: int
    total_pages: int
