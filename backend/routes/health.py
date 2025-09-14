from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional, Literal
import os
from pathlib import Path

# Import the HealthQA class
from health_qa import HealthQA

router = APIRouter(prefix="/api/health", tags=["health"])

# Initialize the health QA system
knowledge_file = Path(__file__).parent.parent / "medical_knowledge.json"
health_qa = HealthQA(str(knowledge_file))

class HealthQuestion(BaseModel):
    question: str
    language: Literal["en", "ak"] = "en"  # Support both English and Akan

@router.post("/ask")
async def ask_health_question(question_data: HealthQuestion):
    """
    Answer health-related questions based on the knowledge base.
    
    Request body:
    - question: The health-related question to answer
    - language: Language code ('en' for English, 'ak' for Akan)
    
    Returns:
    - JSON response with the answer and metadata in the requested language
    """
    try:
        # Get the answer from the HealthQA system
        answer = health_qa.answer_question(
            question=question_data.question,
            language=question_data.language
        )
        
        return {
            "success": True,
            "response": answer,
            "question": question_data.question,
            "language": question_data.language
        }
        
    except Exception as e:
        error_msg = "Yɛnnye asɛm no nti yɛsrɛ wo san bisis" if question_data.language == 'ak' \
                  else "Failed to process your question"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": error_msg,
                "details": str(e)
            }
        )

# Add a simple health check endpoint
@router.get("/status")
async def health_check(
    language: Literal["en", "ak"] = Query("en", description="Response language (en/ak)")
):
    """Check if the health QA service is running."""
    status_msg = "Ɛyɛ" if language == 'ak' else "healthy"
    service_name = "Yarehwɛfoɔ" if language == 'ak' else "Health QA"
    
    return {
        "status": status_msg,
        "service": service_name,
        "language": language,
        "knowledge_base": {
            "diseases_loaded": len(health_qa.disease_names) > 0,
            "disease_count": len(health_qa.disease_names),
            "supported_languages": ["en", "ak"]
        }
    }
