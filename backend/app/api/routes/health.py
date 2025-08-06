from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from typing import Optional
import time
import uuid
import os
import tempfile
import logging

# Set up logging
logger = logging.getLogger(__name__)

from app.core.database import get_mongodb, create_health_query, User
from app.core.auth import get_current_user_optional
from app.models.schemas import (
    HealthQueryRequest, HealthQueryResponse,
    AudioQueryRequest, AudioQueryResponse
)

router = APIRouter()

@router.post("/ask", response_model=HealthQueryResponse)
async def ask_health_question(
    query: HealthQueryRequest,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Process health question and return AI-generated response with Akan language support
    
    Supports both English and Akan (ak) languages. Auto-detects language if not specified.
    """
    start_time = time.time()
    query_id = str(uuid.uuid4())
    
    try:
        # Log the incoming request
        logger.info(f"[Health Query {query_id}] Received question: {query.question[:200]}... (lang: {query.language or 'auto'})")
        
        # Validate input
        if not query.question or not query.question.strip():
            error_msg = "Question cannot be empty"
            logger.warning(f"[Health Query {query_id}] {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Get AI manager from app state
        try:
            ai_manager = request.app.state.ai_manager
            if not ai_manager:
                error_msg = "AI manager not initialized"
                logger.error(f"[Health Query {query_id}] {error_msg}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=error_msg
                )
                
            if not hasattr(ai_manager, '_ready') or not ai_manager._ready:
                error_msg = "AI service is initializing. Please try again in a moment."
                logger.warning(f"[Health Query {query_id}] {error_msg}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=error_msg
                )
        except Exception as e:
            logger.error(f"[Health Query {query_id}] Error initializing AI manager: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error initializing AI service: {str(e)}"
            )
        
        # Generate response using AI with context if provided
        try:
            logger.debug(f"[Health Query {query_id}] Generating response...")
            ai_response = await ai_manager.generate_medical_response(
                question=query.question,
                language=query.language,
                context=getattr(query, 'context', None)
            )
            
            if not ai_response or not isinstance(ai_response, dict) or "answer" not in ai_response:
                error_msg = "Invalid response from AI service"
                logger.error(f"[Health Query {query_id}] {error_msg}. Response: {ai_response}")
                raise ValueError(error_msg)
                
            # Ensure response has all required fields
            ai_response["response"] = ai_response.pop("answer", "No answer provided")
            
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"[Health Query {query_id}] Error generating response: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating response: {str(e)}"
            )
        
        # Create query record with additional metadata
        try:
            query_data = {
                "query_id": query_id,
                "user_id": str(current_user.id) if current_user else None,
                "query_text": query.question,
                "query_language": query.language or "auto",
                "response_text": ai_response.get("response", ""),
                "response_language": ai_response.get("language", query.language or "en"),
                "source": ai_response.get("source", "Akan Medical AI"),
                "is_emergency": ai_response.get("is_emergency", False),
                "timestamp": ai_response.get("timestamp", time.time()),
                "processing_time": time.time() - start_time,
                "model_used": ai_response.get("model_used", "unknown")
            }
            
            await create_health_query(query_data)
            logger.debug(f"[Health Query {query_id}] Saved to database")
            
        except Exception as e:
            logger.error(f"[Health Query {query_id}] Error saving to database: {str(e)}", exc_info=True)
            # Continue even if database save fails
        
        # Log to MongoDB for analytics
        try:
            processing_time = time.time() - start_time
            await log_query_to_mongodb(
                query_id=query_id,
                user_id=current_user.id if current_user else None,
                query_data=query.dict(),
                response_data=ai_response,
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"[Health Query {query_id}] Error logging to MongoDB: {str(e)}", exc_info=True)
            # Continue even if analytics logging fails
        
        # Create response object with all required fields
        try:
            response_data = {
                "response": ai_response["response"],
                "confidence": float(ai_response.get("confidence", 0.8)),  # Ensure float type
                "language": ai_response.get("language", "en"),
                "model_used": ai_response.get("source", "Local Knowledge Base"),
                "query_id": query_id
            }
            
            logger.info(f"[Health Query {query_id}] Successfully processed in {time.time() - start_time:.2f}s")
            return HealthQueryResponse(**response_data)
            
        except Exception as e:
            logger.error(f"[Health Query {query_id}] Error preparing response: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error preparing response: {str(e)}"
            )
        
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions with their original status code
        logger.error(
            f"[Health Query {query_id}] HTTP {http_exc.status_code} error: {str(http_exc.detail)}",
            exc_info=True
        )
        raise http_exc
        
    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"[Health Query {query_id}] {error_msg}", exc_info=True)
        
        # Log error to MongoDB
        try:
            await log_error_to_mongodb(
                user_id=current_user.id if current_user else None,
                query_data=query.dict() if 'query' in locals() else {},
                error=error_msg,
                processing_time=time.time() - start_time
            )
        except Exception as log_error:
            logger.error(f"[Health Query {query_id}] Error logging error to MongoDB: {str(log_error)}", exc_info=True)
        
        # Return a user-friendly error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to process health question",
                "message": "An unexpected error occurred. Please try again later.",
                "request_id": query_id,
                "timestamp": time.time()
            }
        )

@router.post("/ask-audio", response_model=AudioQueryResponse)
async def ask_health_question_audio(
    audio_file: UploadFile = File(...),
    language: str = "auto",
    include_translation: bool = True,
    request: Request = None,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Process audio health question and return AI-generated response"""
    
    start_time = time.time()
    
    try:
        # Validate audio file
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an audio file"
            )
        
        # Get AI manager
        ai_manager = request.app.state.ai_manager
        if not ai_manager or not ai_manager.is_ready():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is not ready. Please try again later."
            )
        
        # Save audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe audio (mock implementation)
            transcription_result = await ai_manager.transcribe_audio(temp_file_path)
            transcribed_text = transcription_result["text"]
            transcription_language = transcription_result.get("language", "unknown")
            
            # Generate health response
            ai_response = await ai_manager.generate_medical_response(
                question=transcribed_text,
                language=language if language != "auto" else transcription_language
            )
            
            # Create query record
            query_id = str(uuid.uuid4())
            query_data = {
                "user_id": current_user.id if current_user else None,
                "query_text": transcribed_text,
                "query_language": transcription_language,
                "response_text": ai_response["response"],
                "response_language": ai_response.get("language", "en"),
                "confidence_score": str(ai_response.get("confidence", 0.0)),
                "model_used": f"audio_transcription+{ai_response.get('model_used', 'unknown')}"
            }
            
            await create_health_query(query_data)
            
            # Log to MongoDB
            processing_time = time.time() - start_time
            await log_query_to_mongodb(
                query_id=query_id,
                user_id=current_user.id if current_user else None,
                query_data={
                    "audio_file": audio_file.filename,
                    "transcribed_text": transcribed_text,
                    "language": language
                },
                response_data=ai_response,
                processing_time=processing_time
            )
            
            return AudioQueryResponse(
                transcription=transcribed_text,
                transcription_language=transcription_language,
                response=ai_response["response"],
                confidence=ai_response.get("confidence", 0.0),
                language=ai_response.get("language", "en"),
                model_used=f"audio_transcription+{ai_response.get('model_used', 'unknown')}",
                query_id=query_id
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        processing_time = time.time() - start_time
        await log_error_to_mongodb(
            user_id=current_user.id if current_user else None,
            query_data={"audio_file": audio_file.filename, "language": language},
            error=str(e),
            processing_time=processing_time
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing audio question: {str(e)}"
        )

async def log_query_to_mongodb(
    query_id: str,
    user_id: Optional[str],
    query_data: dict,
    response_data: dict,
    processing_time: float
):
    """Log query to MongoDB for analytics"""
    try:
        mongodb = await get_mongodb()
        if mongodb:
            log_entry = {
                "query_id": query_id,
                "user_id": user_id,
                "query_data": query_data,
                "response_data": response_data,
                "processing_time": processing_time,
                "timestamp": time.time(),
                "type": "query"
            }
            await mongodb.query_logs.insert_one(log_entry)
    except Exception as e:
        print(f"Error logging to MongoDB: {e}")

async def log_error_to_mongodb(
    user_id: Optional[str],
    query_data: dict,
    error: str,
    processing_time: float
):
    """Log error to MongoDB"""
    try:
        mongodb = await get_mongodb()
        if mongodb:
            log_entry = {
                "user_id": user_id,
                "query_data": query_data,
                "error": error,
                "processing_time": processing_time,
                "timestamp": time.time(),
                "type": "error"
            }
            await mongodb.error_logs.insert_one(log_entry)
    except Exception as e:
        print(f"Error logging error to MongoDB: {e}")
