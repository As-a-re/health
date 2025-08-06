from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from app.core.auth import get_current_active_user
from app.core.database import get_user_health_queries, get_mongodb, User
from app.models.schemas import UserResponse, UserUpdate, HealthQueryHistory

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get user profile"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        preferred_language=current_user.preferred_language,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update user profile"""
    mongodb = await get_mongodb()
    
    update_data = {}
    if user_update.full_name is not None:
        update_data["full_name"] = user_update.full_name
    if user_update.preferred_language is not None:
        update_data["preferred_language"] = user_update.preferred_language
    
    if update_data:
        await mongodb.users.update_one(
            {"_id": current_user.id},
            {"$set": update_data}
        )
        
        # Update current user object
        for key, value in update_data.items():
            setattr(current_user, key, value)
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        preferred_language=current_user.preferred_language,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

@router.get("/history", response_model=HealthQueryHistory)
async def get_user_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's health query history"""
    skip = (page - 1) * page_size
    queries, total_count = await get_user_health_queries(
        current_user.id, skip=skip, limit=page_size
    )
    
    query_items = []
    for query in queries:
        query_items.append({
            "id": query.id,
            "query_text": query.query_text,
            "query_language": query.query_language,
            "response_text": query.response_text,
            "response_language": query.response_language,
            "confidence_score": query.confidence_score,
            "model_used": query.model_used,
            "created_at": query.created_at.isoformat()
        })
    
    return HealthQueryHistory(
        queries=query_items,
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=(total_count + page_size - 1) // page_size
    )

@router.delete("/history/{query_id}")
async def delete_query(
    query_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a specific health query"""
    mongodb = await get_mongodb()
    
    result = await mongodb.health_queries.delete_one({
        "_id": query_id,
        "user_id": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    return {"message": "Query deleted successfully"}

@router.get("/stats")
async def get_user_stats(current_user: User = Depends(get_current_active_user)):
    """Get user statistics"""
    mongodb = await get_mongodb()
    
    # Get total queries count
    total_queries = await mongodb.health_queries.count_documents({
        "user_id": current_user.id
    })
    
    # Get queries by language
    pipeline = [
        {"$match": {"user_id": current_user.id}},
        {"$group": {
            "_id": "$query_language",
            "count": {"$sum": 1}
        }}
    ]
    
    language_stats = {}
    async for doc in mongodb.health_queries.aggregate(pipeline):
        language_stats[doc["_id"]] = doc["count"]
    
    # Get recent activity (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    recent_queries = await mongodb.health_queries.count_documents({
        "user_id": current_user.id,
        "created_at": {"$gte": thirty_days_ago}
    })
    
    return {
        "total_queries": total_queries,
        "recent_queries": recent_queries,
        "language_breakdown": language_stats,
        "member_since": current_user.created_at.isoformat()
    }
