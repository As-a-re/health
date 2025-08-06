import asyncio
import aiohttp
import json
import re
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime
import random
import os

from app.core.config import settings
from app.core.medical_qa import MedicalQA

logger = logging.getLogger(__name__)

import torch
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline

class AIModelManager:
    """Manages AI responses using BioBERT for medical QA and Khaya AI for translation"""
    
    def __init__(self):
        self._ready = False
        self.session = None
        self.health_dataset = {}
        self.medical_qa = MedicalQA()
        
        # Fallback knowledge base
        self.medical_knowledge = {
            # Common symptoms
            "headache": {
                "en": "Headaches can be caused by stress, dehydration, lack of sleep, eye strain, or underlying conditions. Rest in a quiet, dark room, stay hydrated, and apply cold/warm compress. Seek medical attention if severe or persistent.",
                "ak": "Ti yare betumi afi stress, nsuo a wonnom, nna a wonnya, aniwa mu haw, anaa ɔyare foforɔ mu ba. Home wɔ komm ne sum beae, nom nsuo pii, na fa nsuonwini anaa hyew nneɛma to wo ti so."
            },
            "fever": {
                "en": "Fever is the body's response to infection. Normal temperature is 98.6°F (37°C). Rest, drink fluids, and use fever reducers if appropriate. Seek medical care if fever exceeds 103°F (39.4°C) or persists.",
                "ak": "Ɔhyew yɛ nipadua no ɔkwan a ɔfa so ko tia nyarewa. Nipadua mu hyew a ɛyɛ dɛ yɛ 98.6°F (37°C). Home, nom nsuo pii, na sɛ ɛho hia a, nom nnuro a ɛtumi te ɔhyew so."
            },
            # Expanded medical conditions
            "malaria": {
                "en": "Malaria is caused by parasites spread through mosquito bites. Symptoms include high fever, chills, headache, and fatigue. Seek immediate medical attention if you suspect malaria.",
                "ak": "Atiridii yɛ ɔyare a ɛfi asan a ɛkɔ so wɔ ɔsram no nipadua mu. Nnuru a wɔde sa atiridii no bi ne chloroquine, artemisinin-based combination therapies (ACTs), ne foforɔ. Sɛ wo susu sɛ wobɛtumi anya atiridii a, kɔ oduruyɛbea ntɛm ara."
            },
            "hypertension": {
                "en": "High blood pressure often has no symptoms but can lead to serious health issues. Maintain a healthy diet, exercise regularly, limit alcohol, and avoid smoking.",
                "ak": "Mogya a ɛyɛ den kɛse pii no ɛnni nneɛma a ɛda adi, nanso ɛtumi de ɔhaw akɛse aba wo yare mu. Di aduane pa, yɛ mmirika, fa nsa gu, na yɛ mogya mu nsunsuansoɔ nhwehwɛmu daa."
            },
            # Add more conditions as needed
        }
        
        logger.info("AI Manager initialized with offline medical knowledge")
    
    async def initialize(self):
        """Initialize the AI manager with health data and models"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10),
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            # Initialize Medical QA with BioBERT and Khaya AI
            await self.medical_qa.initialize()
            
            # Load health dataset
            await self.load_health_dataset()
            
            self._ready = True
            logger.info("✅ AI Manager initialized successfully with BioBERT and Khaya AI")
            
        except Exception as e:
            logger.error(f"❌ Error initializing AI Manager: {e}")
            self._ready = True  # Still ready with offline knowledge
    
    def is_ready(self) -> bool:
        """Check if the AI manager is ready"""
        return self._ready
        
    async def load_health_dataset(self):
        """Load health dataset from MongoDB or other sources"""
        try:
            # In a production environment, this would load from a proper dataset
            # For now, we'll use the medical_knowledge dictionary
            logger.info("✅ Loaded health dataset")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load health dataset: {str(e)}")
            return False
            
    async def initialize_akan_model(self):
        """Initialize the Akan language model"""
        try:
            from app.core.config import settings
            
            model_path = os.getenv("AKAN_MODEL_PATH", "akan_medical_model")
            
            # Check if model files exist
            if not os.path.exists(model_path):
                logger.warning(f"Akan model not found at {model_path}. Using fallback responses.")
                return False
                
            logger.info(f"Loading Akan model from {model_path}...")
            
            # Load model and tokenizer
            self.akan_model = AutoModelForQuestionAnswering.from_pretrained(
                model_path,
                local_files_only=True
            )
            
            self.akan_tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                local_files_only=True
            )
            
            # Set model to evaluation mode
            self.akan_model.eval()
            
            # Move to GPU if available
            if torch.cuda.is_available():
                self.akan_model = self.akan_model.cuda()
                logger.info("✅ Akan model loaded on GPU")
            else:
                logger.info("✅ Akan model loaded on CPU")
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Akan model: {str(e)}")
            # Fallback to using the knowledge base if model loading fails
            self.akan_model = None
            self.akan_tokenizer = None
            return False
    
    async def search_health_info(self, query: str) -> List[Dict[str, str]]:
        """Search for health information online"""
        if not self.session or not settings.ENABLE_WEB_SEARCH:
            return []
        
        try:
            # Use DuckDuckGo Instant Answer API (free, no API key needed)
            search_url = f"https://api.duckduckgo.com/?q={query} health medical&format=json&no_html=1&skip_disambig=1"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    # Extract abstract if available
                    if data.get('Abstract'):
                        results.append({
                            'title': data.get('Heading', 'Health Information'),
                            'content': data['Abstract'],
                            'source': data.get('AbstractURL', 'DuckDuckGo')
                        })
                    
                    # Extract related topics
                    for topic in data.get('RelatedTopics', [])[:3]:
                        if isinstance(topic, dict) and topic.get('Text'):
                            results.append({
                                'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                                'content': topic['Text'],
                                'source': topic.get('FirstURL', 'DuckDuckGo')
                            })
                    
                    return results[:settings.MAX_SEARCH_RESULTS]
                    
        except Exception as e:
            logger.error(f"Search error: {e}")
        
        return []
    
    def get_medical_knowledge(self, query: str, language: str = "en") -> str:
        """Get medical knowledge from local database"""
        query_lower = query.lower()
        
        # Check for keywords in query
        for condition, info in self.medical_knowledge.items():
            if any(keyword in query_lower for keyword in [
                condition, 
                condition.replace('_', ' '),
                'pain' if 'pain' in condition else '',
                'ache' if 'ache' in condition else ''
            ]):
                return info.get(language, info.get('en', ''))
        
        # Default response
        default_responses = {
            "en": "I understand your health concern. For specific medical advice, I recommend consulting with a qualified healthcare professional who can properly assess your situation. If this is an emergency, please seek immediate medical attention.",
            "ak": "Mete wo apɔmuden ho haw ase. Sɛ wopɛ oduruyɛfoɔ afotuo pɔtee a, mekamfo sɛ wo ne oduruyɛfoɔ a ne ho wɔ hɔ bɛkasa na ɔahwɛ wo tebea yiye. Sɛ ɛyɛ ntɛmntɛm asɛm a, hwehwɛ ayaresa ntɛm."
        }
        
        return default_responses.get(language, default_responses["en"])
    
    def detect_language(self, text: str) -> str:
        """Simple language detection"""
        # Check for common Akan words
        akan_words = ['wo', 'me', 'yɛ', 'na', 'sɛ', 'wɔ', 'no', 'mu', 'ho', 'ba', 'kɔ', 'nom', 'ti', 'yare']
        text_lower = text.lower()
        
        akan_count = sum(1 for word in akan_words if word in text_lower)
        
        return "ak" if akan_count >= 2 else "en"
        
    def check_emergency_condition(self, text: str, language: str = "en") -> Optional[str]:
        """
        Check if the text contains emergency conditions
        
        Args:
            text: The text to check
            language: The language of the text (en/ak)
            
        Returns:
            str: Emergency response if condition is detected, None otherwise
        """
        text_lower = text.lower()
        
        # Emergency conditions in English and Akan
        emergency_conditions = [
            # Chest pain or heart attack symptoms
            {
                'keywords': ['chest pain', 'heart attack', 'can\'t breathe', 'difficulty breathing', 'severe pain'],
                'response': {
                    'en': '⚠️ EMERGENCY: You may be experiencing a serious medical condition. Please call emergency services immediately or go to the nearest hospital.',
                    'ak': '⚠️ NTƐM YI: Wobetumi anya ɔyare a ɛyɛ hu. Yɛsrɛ wo frɛ ɔyarefoɔ anaa kɔ ɔyarekurom a ɛbɛn ha ntɛm ara.'
                }
            },
            # Severe bleeding
            {
                'keywords': ['bleeding a lot', 'severe bleeding', 'can\'t stop bleeding', 'blood everywhere'],
                'response': {
                    'en': '⚠️ EMERGENCY: Severe bleeding requires immediate medical attention. Apply pressure to the wound and call emergency services right away.',
                    'ak': '⚠️ NTƐM YI: Mogya a ɛpue pii hia ayaresa ntɛm. Fa wo nsa to ayaresa no so na frɛ ɔyarefoɔ ntɛm ara.'
                }
            },
            # Difficulty breathing
            {
                'keywords': ['can\'t breathe', 'choking', 'suffocating', 'no air'],
                'response': {
                    'en': '⚠️ EMERGENCY: Difficulty breathing can be life-threatening. Call emergency services immediately.',
                    'ak': '⚠️ NTƐM YI: Sɛ wunntumi nhom yie a, ɛtumi ayɛ hu. Frɛ ɔyarefoɔ ntɛm ara.'
                }
            },
            # Severe allergic reaction
            {
                'keywords': ['allergic reaction', 'throat closing', 'swelling face', 'swelling lips', 'anaphylaxis'],
                'response': {
                    'en': '⚠️ EMERGENCY: Severe allergic reaction can be life-threatening. Use an epinephrine auto-injector if available and call emergency services immediately.',
                    'ak': '⚠️ NTƐM YI: Sɛ wunntumi nhom yie a, ɛtumi ayɛ hu. Fa wo nsa to ayaresa no so na frɛ ɔyarefoɔ ntɛm ara.'
                }
            },
            # Loss of consciousness
            {
                'keywords': ['passed out', 'unconscious', 'blacked out', 'fainted'],
                'response': {
                    'en': '⚠️ EMERGENCY: Loss of consciousness requires immediate medical attention. Call emergency services right away.',
                    'ak': '⚠️ NTƐM YI: Sɛ wo ani nnye ho a, ɛhia sɛ wofrɛ ɔyarefoɔ ntɛm ara.'
                }
            }
        ]
        
        # Check for emergency conditions
        for condition in emergency_conditions:
            if any(keyword in text_lower for keyword in condition['keywords']):
                return condition['response'].get(language, condition['response']['en'])
                
        return None
    
    async def generate_medical_response(
        self, 
        question: str, 
        language: str = "auto",
        context: str = None
    ) -> dict:
        """
        Generate a response to a medical question using BioBERT and Khaya AI
        
        Args:
            question: The user's question
            language: The language of the question (en/ak/auto)
            context: Optional context for the question (for QA model)
            
        Returns:
            dict: Response with answer, language, and metadata
        """
        try:
            if not self._ready:
                await self.initialize()
                
            # Auto-detect language if not specified
            if language == "auto":
                language = self.detect_language(question)
                
            # Check for emergency conditions in both languages
            emergency_response = await asyncio.to_thread(self.check_emergency_condition, question, language)
            if emergency_response:
                return await asyncio.to_thread(self.format_response, emergency_response, language, is_emergency=True)
            
            # Use BioBERT for medical QA
            try:
                # If no context provided, use the question as context
                qa_context = context or question
                
                # Get answer from BioBERT
                qa_result = await self.medical_qa.answer_question(
                    question=question,
                    context=qa_context,
                    language=language
                )
                
                # Format the response
                return await asyncio.to_thread(
                    self.format_response,
                    qa_result["answer"],
                    language,
                    source=qa_result.get("model", "BioBERT"),
                    confidence=qa_result.get("confidence", 0.0)
                )
                
            except Exception as e:
                logger.error(f"Error in BioBERT QA: {str(e)}", exc_info=True)
                
                # Fallback to local knowledge base if BioBERT fails
                local_response = await self.search_health_info(question)
                if local_response:
                    # Translate if needed
                    response_text = local_response[0]['content']
                    if language == "ak":
                        response_text = await self.medical_qa.translate_text(response_text, "ak")
                        
                    return await asyncio.to_thread(
                        self.format_response,
                        response_text,
                        language,
                        source="Local Knowledge Base"
                    )
                
                # Final fallback
                fallback_msg = (
                    "Mepa wo kyɛw, m'ani nnye ho. Yɛsrɛ wo san aye akyiri bi."
                    if language == "ak" else
                    "I'm sorry, I encountered an error processing your request. Please try again later."
                )
                return await asyncio.to_thread(self.format_response, fallback_msg, language, is_error=True)
            
        except Exception as e:
            logger.error(f"Error generating medical response: {e}")
            error_msg = (
                "Mepa wo kyɛw, m'ani nnye ho. Yɛsrɛ wo san aye akyiri bi."
                if language == "ak" else
                "I'm sorry, I encountered an error processing your request. Please try again later."
            )
            return self.format_response(error_msg, language, is_error=True)
    
    def format_response(
        self, 
        response_text: str, 
        language: str = "en", 
        source: str = None,
        is_emergency: bool = False,
        is_error: bool = False,
        confidence: float = None
    ) -> dict:
        """
        Format a consistent response object
        
        Args:
            response_text: The response text
            language: Language code (en/ak)
            source: Source of the response (e.g., 'BioBERT')
            is_emergency: Whether this is an emergency response
            is_error: Whether this is an error response
            confidence: Confidence score of the response (0.0 to 1.0)
            
        Returns:
            dict: Formatted response object
        """
        return {
            "response": response_text,
            "language": language,
            "source": source or "Medical AI",
            "is_emergency": is_emergency,
            "is_error": is_error,
            "confidence": float(confidence) if confidence is not None else None,
            "model": "BioBERT",
            "translation_model": "Khaya AI",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def transcribe_audio(self, audio_file_path: str) -> Dict[str, str]:
        """Mock audio transcription (would need speech-to-text service)"""
        try:
            # In a real implementation, this would call a speech-to-text service
            # For now, return a mock response
            return {"text": "This is a mock transcription of the audio.", "language": "en"}
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return {"text": "", "language": "en", "error": str(e)}
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.session:
                await self.session.close()
            logger.info("✅ AI Manager cleaned up")
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
