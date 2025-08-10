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
            # Infectious diseases
            "malaria": {
                "en": "Malaria is caused by parasites spread through mosquito bites. Symptoms include high fever, chills, headache, and fatigue. Seek immediate medical attention if you suspect malaria.",
                "ak": "Atiridii yɛ ɔyare a ɛfi asan a ɛkɔ so wɔ ɔsram no nipadua mu. Nnuru a wɔde sa atiridii no bi ne chloroquine, artemisinin-based combination therapies (ACTs), ne foforɔ. Sɛ wo susu sɛ wobɛtumi anya atiridii a, kɔ oduruyɛbea ntɛm ara."
            },
            "covid": {
                "en": "COVID-19 is a viral respiratory illness. Symptoms include cough, fever, loss of taste/smell, and shortness of breath. Prevent by wearing masks, washing hands, and vaccination.",
                "ak": "COVID-19 yɛ yare a ɛfa mframa mu. N'nsɛnhunu ne su, ɔhyew, dɛdɛɛdɛ ne ahomeguare. To ho ban fa mask, hohor wo nsam, na yɛ vaccine."
            },
            "tuberculosis": {
                "en": "Tuberculosis (TB) is an infectious disease affecting the lungs. Symptoms: persistent cough, weight loss, night sweats. Treatment requires long-term antibiotics.",
                "ak": "Tuberculosis yɛ yare a ɛtɔ mmirika na ɛka nipadua mu. Nsɛnhunu: su a ɛnnware, nipadua mu fam, anadwo susu. Yare yi hia nnuro a wobɛfa akyɛ."
            },
            "typhoid": {
                "en": "Typhoid fever is caused by Salmonella bacteria, spread through contaminated food/water. Symptoms: high fever, abdominal pain, diarrhea. Treat with antibiotics.",
                "ak": "Typhoid yɛ yare a ɛfi nsuo anaa aduane a ɛho ntew so. Nsɛnhunu: ɔhyew kɛse, yafunu yare, nsu. Fa nnuro kɔhwehwɛ oduruyɛfoɔ."
            },

            # Chronic diseases
            "diabetes": {
                "en": "Diabetes is a chronic condition where blood sugar is too high. Symptoms: frequent urination, thirst, fatigue. Managed by diet, exercise, and medication.",
                "ak": "Sukɔm yɛ ɔyare a mogya mu sukuruwa dɔɔso. Nsɛnhunu: nsuo a wopɛ dodo, home, brɛ. Di aduane pa, yɛ mmirika, na fa nnuro."
            },
            "asthma": {
                "en": "Asthma is a condition where airways narrow and swell. Symptoms: wheezing, coughing, chest tightness. Use inhalers and avoid triggers.",
                "ak": "Asthma yɛ yare a ɛma mframa kwan to. Nsɛnhunu: ahomeguare, su, yafunu mu den. Fa inhaler na to ho ban."
            },
            "sickle cell": {
                "en": "Sickle cell disease affects red blood cells, causing pain, anemia, and infections. Seek regular medical care and stay hydrated.",
                "ak": "Sickle cell yɛ yare a ɛka mogya mu. Ede yaw, mogya mu fam, ne yare foforɔ ba. Kɔ oduruyɛbea daa na nom nsuo pii."
            },
            "hypertension": {
                "en": "High blood pressure often has no symptoms but can lead to serious health issues. Maintain a healthy diet, exercise regularly, limit alcohol, and avoid smoking.",
                "ak": "Mogya a ɛyɛ den kɛse pii no ɛnni nneɛma a ɛda adi, nanso ɛtumi de ɔhaw akɛse aba wo yare mu. Di aduane pa, yɛ mmirika, fa nsa gu, na yɛ mogya mu nsunsuansoɔ nhwehwɛmu daa."
            },

            # Symptoms
            "headache": {
                "en": "Headaches can be caused by stress, dehydration, lack of sleep, eye strain, or underlying conditions. Rest in a quiet, dark room, stay hydrated, and apply cold/warm compress. Seek medical attention if severe or persistent.",
                "ak": "Ti yare betumi afi stress, nsuo a wonnom, nna a wonnya, aniwa mu haw, anaa ɔyare foforɔ mu ba. Home wɔ komm ne sum beae, nom nsuo pii, na fa nsuonwini anaa hyew nneɛma to wo ti so."
            },
            "fever": {
                "en": "Fever is the body's response to infection. Normal temperature is 98.6°F (37°C). Rest, drink fluids, and use fever reducers if appropriate. Seek medical care if fever exceeds 103°F (39.4°C) or persists.",
                "ak": "Ɔhyew yɛ nipadua no ɔkwan a ɔfa so ko tia nyarewa. Nipadua mu hyew a ɛyɛ dɛ yɛ 98.6°F (37°C). Home, nom nsuo pii, na sɛ ɛho hia a, nom nnuro a ɛtumi te ɔhyew so."
            },
            "cough": {
                "en": "Coughing helps clear the airways. It can be caused by infection, allergies, or irritants. If cough persists more than 2 weeks, see a doctor.",
                "ak": "Su boa ma mframa kwan ho tew. Ɛbetumi afi yare, allergies, anaa nneɛma a ɛhaw. Sɛ su no to so kyɛ, kɔhwehwɛ oduruyɛfoɔ."
            },
            "vomiting": {
                "en": "Vomiting can be caused by infections, food poisoning, or other illnesses. Stay hydrated and seek medical advice if severe or persistent.",
                "ak": "Nsii betumi afi yare, aduane a ɛho ntew, anaa ɔyare foforɔ. Nom nsuo pii na kɔhwehwɛ oduruyɛfoɔ."
            },
            "rash": {
                "en": "Skin rashes can be caused by allergies, infections, or irritants. Keep the area clean and dry. Seek medical care if spreading or severe.",
                "ak": "Mmogya betumi afi allergies, yare, anaa nneɛma a ɛhaw. Hwɛ sɛ ɛda ho fɛ na ɛyɛ hyew. Sɛ ɛtrɛw anaa ɛyɛ den a, kɔhwehwɛ oduruyɛfoɔ."
            },

            # Treatments
            "paracetamol": {
                "en": "Paracetamol is used to reduce pain and fever. Follow dosage instructions and do not exceed the recommended amount.",
                "ak": "Paracetamol yɛ aduro a wɔde twa yaw ne ɔhyew so. Di kyerɛwsɛm so na mmfa dodo."
            },
            "oral rehydration": {
                "en": "Oral rehydration solution (ORS) treats dehydration, especially from diarrhea. Mix clean water, salt, and sugar as instructed.",
                "ak": "ORS boa ma nsuo a ɛyera fi nipadua mu san ba. Fa nsuo, nkyene ne sukuruwa bɔ bom sɛnea wɔkyerɛ."
            },
            "antibiotics": {
                "en": "Antibiotics treat bacterial infections. Only use when prescribed by a doctor. Do not misuse or overuse.",
                "ak": "Antibiotics yɛ nnuro a wɔde sa yare a ɛfi bacteria mu. Fa no sɛ oduruyɛfoɔ pɛ na mmfa dodo."
            },

            # Preventive advice
            "hand washing": {
                "en": "Wash your hands regularly with soap and water to prevent infections.",
                "ak": "Hohor wo nsam daa fa samina ne nsuo so na to ban yare."
            },
            "vaccination": {
                "en": "Vaccines protect against many diseases. Make sure you and your children are up to date on all vaccinations.",
                "ak": "Vaccine boa ma yare pii ho ban. Hwɛ sɛ wo ne wo mma anya vaccine a ehia."
            },
        }

    def retrieve_best_context(self, question: str, language: str = "en") -> str:
        """
        Improved retrieval: returns the best matching passage from the knowledge base for the question.
        Now robust to punctuation, plural/singular, and common question forms.
        """
        import re
        import logging
        logger = logging.getLogger(__name__)
        # Normalize question: lowercase, remove punctuation
        normalized_question = re.sub(r'[^a-zA-Z0-9\s]', '', question.lower())
        question_words = set(re.findall(r"\w+", normalized_question))
        best_score = 0
        best_entry = None
        best_key = None
        for key, entry in self.medical_knowledge.items():
            # Normalize key (disease/symptom)
            key_norm = re.sub(r'[^a-zA-Z0-9\s]', '', key.lower())
            entry_words = set(re.findall(r"\w+", key_norm))
            overlap = question_words & entry_words
            score = len(overlap)
            # Bonus if key appears as a word or at end of question (e.g., 'malaria' in 'symptoms of malaria')
            if re.search(rf'\b{re.escape(key_norm)}\b', normalized_question):
                score += 3
            elif normalized_question.endswith(key_norm):
                score += 2
            # Bonus for substring match (legacy)
            elif key_norm in normalized_question:
                score += 1
            if score > best_score:
                best_score = score
                best_entry = entry[language] if language in entry else entry.get("en", "")
                best_key = key
        logger.debug(f"[retrieve_best_context] Q: '{question}' | Matched: '{best_key}' | Score: {best_score}")
        if best_score >= 1 and best_entry:
            return best_entry
        return None

        
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
        Generate a response to a medical question using BioBERT with fallback to local knowledge
        
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
            
            # Ensure MedicalQA is initialized
            if not hasattr(self.medical_qa, 'initialized') or not self.medical_qa.initialized:
                await self.medical_qa.initialize()
                
            # Auto-detect language if not specified
            if language == "auto":
                language = self.detect_language(question)
            
            # Ensure we have a valid language
            if language not in ["en", "ak"]:
                language = "en"
                
            # Check for emergency conditions
            emergency_response = self.check_emergency_condition(question, language)
            if emergency_response:
                return self.format_response(
                    emergency_response,
                    language,
                    source="Emergency Check",
                    is_emergency=True,
                    confidence=1.0
                )
            
            # Try to get answer from MedicalQA (BioBERT with fallbacks)
            try:
                # Use improved context retrieval for BioBERT
                context_passage = self.retrieve_best_context(question, language)
                qa_result = await self.medical_qa.answer_question(
                    question=question,
                    language=language,
                    context=context_passage
                )
                
                # Log the response for debugging
                logger.info(f"MedicalQA response: {qa_result}")
                
                # If we got a valid response with confidence > 0, use it
                if qa_result.get("confidence", 0) > 0:
                    # Use answer if present, else fallback to response or a default string
                    answer_val = qa_result.get("answer") or qa_result.get("response") or "No answer provided"
                    return self.format_response(
                        answer_val,
                        language=language,
                        source=qa_result.get("source", "BioBERT"),
                        confidence=float(qa_result.get("confidence", 0.0))
                    )
                
                # If low confidence, fall through to local knowledge
                logger.warning(f"Low confidence response from MedicalQA: {qa_result}")
                
            except Exception as e:
                logger.error(f"Error in MedicalQA: {str(e)} | QA result: {locals().get('qa_result', None)}", exc_info=True)
            
            # Fallback 1: Try improved context retrieval (direct answer if not used above)
            try:
                context_passage = self.retrieve_best_context(question, language)
                if context_passage:
                    return self.format_response(
                        context_passage,
                        language=language,
                        source="Local Knowledge Base",
                        confidence=0.7
                    )
            except Exception as e:
                logger.error(f"Error in improved context retrieval fallback: {str(e)}", exc_info=True)
            
            # Fallback 2: Try web search if enabled
            if settings.ENABLE_WEB_SEARCH:
                try:
                    search_results = await self.search_health_info(question)
                    if search_results and len(search_results) > 0:
                        return self.format_response(
                            search_results[0]['content'],
                            language=language,
                            source=search_results[0].get('source', 'Web Search'),
                            confidence=0.6
                        )
                except Exception as e:
                    logger.error(f"Error in web search fallback: {str(e)}", exc_info=True)
            
            # Final fallback: Generic response
            fallback_msg = (
                "Mepa wo kyɛw, m'ani nnye ho. Yɛsrɛ wo san aye akyiri bi anaa kɔbisa oduruyɛfoɔ."
                if language == "ak" else
                "I'm sorry, I couldn't find a specific answer to your question. Please try rephrasing or consult a healthcare professional for medical advice."
            )
            
            return self.format_response(
                fallback_msg,
                language=language,
                source="System",
                confidence=0.1,
                is_error=False
            )
            
        except Exception as e:
            logger.critical(f"Critical error in generate_medical_response: {str(e)}", exc_info=True)
            
            # Critical error response
            error_msg = (
                "Mepa wo kyɛw, ɛsɔreɛ bi baa mu. Yɛsrɛ wo san aye akyiri bi."
                if language == "ak" else
                "I'm sorry, I encountered an unexpected error. Please try again later."
            )
            
            return self.format_response(
                error_msg,
                language=language,
                source="System",
                is_error=True,
                confidence=0.0
            )
    
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
        # Always include both 'answer' and 'response' keys for compatibility
        return {
            "answer": response_text,
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
