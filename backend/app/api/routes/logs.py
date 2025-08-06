from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from datetime import datetime, timedelta

from app.core.database import get_mongodb
from app.core.auth import get_current_active_user
from app.core.database import User
from app.models.schemas import LogsResponse, QueryLog

router = APIRouter()

@router.get("/query-logs")
async def get_query_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get user's query logs with filtering"""
    mongodb = await get_mongodb()
    
    # Build filter
    filter_query = {"user_id": current_user.id}
    
    if start_date or end_date:
        date_filter = {}
        if start_date:
            date_filter["$gte"] = datetime.fromisoformat(start_date.replace('Z', '+00:00')).timestamp()
        if end_date:
            date_filter["$lte"] = datetime.fromisoformat(end_date.replace('Z', '+00:00')).timestamp()
        filter_query["timestamp"] = date_filter
    
    # Get total count
    total_count = await mongodb.query_logs.count_documents(filter_query)
    
    # Get paginated results
    skip = (page - 1) * page_size
    cursor = mongodb.query_logs.find(filter_query).sort("timestamp", -1).skip(skip).limit(page_size)
    
    logs = []
    async for log in cursor:
        logs.append({
            "query_id": log.get("query_id"),
            "query_data": log.get("query_data"),
            "response_data": log.get("response_data"),
            "processing_time": log.get("processing_time"),
            "timestamp": datetime.fromtimestamp(log.get("timestamp", 0)).isoformat(),
            "type": log.get("type")
        })
    
    return {
        "logs": logs,
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_count + page_size - 1) // page_size
    }

@router.get("/analytics")
async def get_user_analytics(current_user: User = Depends(get_current_active_user)):
    """Get user analytics data"""
    mongodb = await get_mongodb()
    
    # Average processing time
    pipeline = [
        {"$match": {"user_id": current_user.id, "type": "query"}},
        {"$group": {
            "_id": None,
            "avg_processing_time": {"$avg": "$processing_time"},
            "total_queries": {"$sum": 1}
        }}
    ]
    
    analytics_result = await mongodb.query_logs.aggregate(pipeline).to_list(1)
    avg_processing_time = analytics_result[0]["avg_processing_time"] if analytics_result else 0
    
    # Queries by model used
    model_pipeline = [
        {"$match": {"user_id": current_user.id, "type": "query"}},
        {"$group": {
            "_id": "$response_data.model_used",
            "count": {"$sum": 1}
        }}
    ]
    
    model_stats = {}
    async for doc in mongodb.query_logs.aggregate(model_pipeline):
        model_stats[doc["_id"] or "unknown"] = doc["count"]
    
    # Daily activity (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_pipeline = [
        {"$match": {
            "user_id": current_user.id,
            "type": "query",
            "timestamp": {"$gte": seven_days_ago.timestamp()}
        }},
        {"$group": {
            "_id": {
                "$dateToString": {
                    "format": "%Y-%m-%d",
                    "date": {"$toDate": {"$multiply": ["$timestamp", 1000]}}
                }
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    daily_activity = {}
    async for doc in mongodb.query_logs.aggregate(daily_pipeline):
        daily_activity[doc["_id"]] = doc["count"]
    
    return {
        "average_processing_time": round(avg_processing_time, 3) if avg_processing_time else 0,
        "model_usage": model_stats,
        "daily_activity": daily_activity
    }

@router.get("/queries", response_model=LogsResponse)
async def get_query_logs_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    language: Optional[str] = None,
    model_used: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get query logs (admin endpoint - in production, add admin role check)"""
    
    try:
        mongodb = await get_mongodb()
        if not mongodb:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Logging database not available"
            )
        
        # Build query filter
        query_filter = {"type": "query"}
        
        if start_date:
            query_filter["timestamp"] = {"$gte": start_date.timestamp()}
        
        if end_date:
            if "timestamp" in query_filter:
                query_filter["timestamp"]["$lte"] = end_date.timestamp()
            else:
                query_filter["timestamp"] = {"$lte": end_date.timestamp()}
        
        if language:
            query_filter["response_data.language"] = language
        
        if model_used:
            query_filter["response_data.model_used"] = model_used
        
        # Get total count
        total_count = await mongodb.query_logs.count_documents(query_filter)
        
        # Get logs with pagination
        skip = (page - 1) * page_size
        cursor = mongodb.query_logs.find(query_filter).sort("timestamp", -1).skip(skip).limit(page_size)
        
        logs = []
        async for log_entry in cursor:
            try:
                query_log = QueryLog(
                    query_id=log_entry["query_id"],
                    user_id=log_entry.get("user_id"),
                    query_text=log_entry["query_data"].get("question", ""),
                    query_language=log_entry["response_data"].get("language", "unknown"),
                    response_text=log_entry["response_data"].get("response", ""),
                    response_language=log_entry["response_data"].get("language", "unknown"),
                    confidence_score=log_entry["response_data"].get("confidence", 0.0),
                    model_used=log_entry["response_data"].get("model_used", "unknown"),
                    processing_time=log_entry.get("processing_time", 0.0),
                    timestamp=datetime.fromtimestamp(log_entry["timestamp"]),
                    metadata=log_entry.get("metadata")
                )
                logs.append(query_log)
            except Exception as e:
                print(f"Error processing log entry: {e}")
                continue
        
        return LogsResponse(
            logs=logs,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving logs: {str(e)}"
        )

@router.get("/errors")
async def get_error_logs_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get error logs (admin endpoint)"""
    
    try:
        mongodb = await get_mongodb()
        if not mongodb:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Logging database not available"
            )
        
        # Build query filter
        query_filter = {"type": "error"}
        
        if start_date:
            query_filter["timestamp"] = {"$gte": start_date.timestamp()}
        
        if end_date:
            if "timestamp" in query_filter:
                query_filter["timestamp"]["$lte"] = end_date.timestamp()
            else:
                query_filter["timestamp"] = {"$lte": end_date.timestamp()}
        
        # Get total count
        total_count = await mongodb.error_logs.count_documents(query_filter)
        
        # Get logs with pagination
        skip = (page - 1) * page_size
        cursor = mongodb.error_logs.find(query_filter).sort("timestamp", -1).skip(skip).limit(page_size)
        
        error_logs = []
        async for log_entry in cursor:
            error_logs.append({
                "user_id": log_entry.get("user_id"),
                "query_data": log_entry.get("query_data"),
                "error": log_entry.get("error"),
                "processing_time": log_entry.get("processing_time"),
                "timestamp": datetime.fromtimestamp(log_entry["timestamp"]).isoformat()
            })
        
        return {
            "error_logs": error_logs,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving error logs: {str(e)}"
        )
