import torch
import aiohttp
import logging
import aiohttp
import json
from typing import Dict, Optional, List
import re

logger = logging.getLogger(__name__)

class MedicalQA:
    """Simplified medical QA system with local knowledge base"""
    
    def __init__(self):
        self.knowledge_base = {
            "malaria": {
                "en": "Malaria is caused by parasites transmitted through mosquito bites. Symptoms include high fever, chills, headache, nausea, vomiting, muscle pain, and fatigue. Severe cases can cause jaundice, seizures, coma, or death if untreated. Seek immediate medical attention if you suspect malaria.",
                "ak": "Atiridii yɛ ɔyare a ɛfi asan a ɔsram tu afi no. Nneɛma a ɛda adi no bi ne ɔhyew kɛse, ahuhusiw, ti yare, ayaresa a ɛma wode kuru, ayaresa a ɛma wo vomit, yare a ɛwɔ mmirika mu, ne ahɔhohia. Sɛ ɛyɛ den a, ɛtumi ama w'ani nkura, wubegye woho, wubehu ahosɛ, anaa wuwu sɛ wunnya ayaresa ntɛm ara. Sɛ wususuw sɛ woanya atiridii a, kɔ oduruyɛbea ntɛm ara."
            },
            "headache": {
                "en": "Headaches can have many causes including stress, tension, dehydration, lack of sleep, or eye strain. Common types include tension headaches, migraines, and cluster headaches. Rest, hydration, and over-the-counter pain relievers may help. See a doctor for severe, persistent, or worsening headaches.",
                "ak": "Ti yare betumi afi ahodwiriw, ahodwiriw a ɛma w'atirimu ayɛ den, nsuo a wonnom, nna a wonnya, anaa aniwa yare. Nnipa pii nya tension headache, migraine, ne cluster headache. Sɛ wuhu ti yare a, home, nom nsuo pii, na di nnuru a wotumi tɔn no bi a ɛbɛyɛ ma wo. Sɛ wo ti yare no yɛ den, ɛnyɛ gyina hɔ, anaa ɛyɛ hu mmerɛw a, kɔ oduruyɛfoɔ hɔ."
            },
            "fever": {
                "en": "Fever is a temporary increase in body temperature, often due to an infection. Normal body temperature is around 98.6°F (37°C). A fever is generally considered to be 100.4°F (38°C) or higher. Rest, stay hydrated, and use fever reducers if needed. Seek medical attention for high fevers (above 103°F/39.4°C) or if fever lasts more than 3 days.",
                "ak": "Ɔhyew yɛ nipadua mu hyew a ɛkɔ soro kakra, ɛtaa fi yare bi nti. Nipadua mu hyew a ɛyɛ dɛ yɛ 98.6°F (37°C). Sɛ nipadua mu hyew no so soro kɔ 100.4°F (38°C) anaa ɛboro saa a, wubetumi aka sɛ ɔhyew. Home, nom nsuo pii, na sɛ ɛho hia a, nom nnuru a ɛtumi te ɔhyew so. Sɛ ɔhyew no so soro kɔ 103°F (39.4°C) anaa ɛboro saa, anaa sɛ ɔhyew no da so abɛboro nnansa 3 a, kɔ oduruyɛfoɔ hɔ."
            }
        }
    
    async def answer_question(self, question: str, language: str = "en") -> Dict[str, any]:
        """
        Answer a medical question using the local knowledge base
        
        Args:
            question: The medical question
            language: Language code (en/ak)
            
        Returns:
            Dict containing answer and metadata
        """
        try:
            # Simple keyword matching for demo purposes
            question_lower = question.lower()
            
            # Check for known conditions
            for condition, response in self.knowledge_base.items():
                if condition in question_lower:
                    return {
                        "answer": response.get(language, response["en"]),
                        "language": language,
                        "confidence": 0.9,
                        "source": "Local Knowledge Base"
                    }
            
            # Fallback response
            fallback = {
                "en": "I'm sorry, I don't have enough information to answer that question. Please consult a healthcare professional for medical advice.",
                "ak": "Mepa wo kyɛw, minni nkyerɛaseɛ a ɛfa saa asɛm no ho. Yɛsrɛ wo kɔ nhwehwɛmufoɔ nkyɛn wɔ ayaresa mu."
            }
            
            return {
                "answer": fallback.get(language, fallback["en"]),
                "language": language,
                "confidence": 0.1,
                "source": "System"
            }
            
        except Exception as e:
            logger.error(f"Error in answer_question: {str(e)}")
            return {
                "answer": "An error occurred while processing your question. Please try again later.",
                "language": language,
                "error": str(e),
                "confidence": 0.0,
                "source": "System"
            }
    
    async def translate_text(self, text: str, target_lang: str = "ak") -> str:
        """Simple translation method (placeholder for actual translation)"""
        # In a real implementation, this would call a translation service
        return text

# Trusted medical sources for web search
TRUSTED_MEDICAL_DOMAINS = [
    'mayoclinic.org',
    'webmd.com',
    'cdc.gov',
    'who.int',
    'nhs.uk',
    'healthline.com',
    'medicalnewstoday.com',
    'hopkinsmedicine.org',
    'medlineplus.gov',
    'whoafro.org',
    'ghanahealthservice.org',
    'moh.gov.gh'
]

class MedicalQA:
    """Handles medical question answering using BioBERT and translation using Khaya AI"""
    
    def __init__(self):
        self.qa_model = None
        self.qa_tokenizer = None
        self.translator = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._initialized = False
        
        # Basic translation dictionary for common medical terms
        self.translation_dict = {
            "headache": "ti yare",
            "fever": "ɔhyew",
            "pain": "yare",
            "medicine": "adurow",
            "doctor": "oduruyɛfoɔ",
            "hospital": "ayaresabea",
            "malaria": "atiridii",
            "symptom": "nneɛma a ɛda adi",
            "treatment": "ayaresa",
            "emergency": "ntɛm mu yare"
        }

    async def initialize(self):
        """Initialize the medical QA and translation models"""
        try:
            # Initialize BioBERT for medical QA
            biobert_model_name = "monologg/biobert_v1.1_pubmed"
            logger.info(f"Loading BioBERT model: {biobert_model_name}")
            
            self.qa_tokenizer = AutoTokenizer.from_pretrained(biobert_model_name)
            self.qa_model = AutoModelForQuestionAnswering.from_pretrained(
                biobert_model_name
            ).to(self.device)
            
            logger.info("✅ BioBERT model loaded successfully")
            
            # Initialize translation (using fallback implementation)
            logger.info("Using fallback translation implementation")
            
            self._initialized = True
            
        except Exception as e:
            logger.error(f"❌ Error initializing MedicalQA: {str(e)}", exc_info=True)
            raise
    
    def is_initialized(self) -> bool:
        """Check if the models are loaded"""
        return self._initialized
    
    async def answer_question(self, question: str, context: str, language: str = "en") -> Dict:
        """
        Answer a medical question using BioBERT
        
        Args:
            question: The medical question
            context: Context or background information
            language: Target language for the answer (en/ak)
            
        Returns:
            Dict containing the answer and metadata
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # If context is the same as question, use the medical knowledge base
            if context == question:
                # Look for specific medical terms in the question
                question_lower = question.lower()
                if 'malaria' in question_lower:
                    answer = "Malaria is caused by parasites transmitted through mosquito bites. Common symptoms include high fever, chills, headache, nausea, vomiting, muscle pain, and fatigue. Severe cases can cause jaundice, seizures, coma, or death if untreated. Seek immediate medical attention if you suspect malaria."
                elif 'headache' in question_lower:
                    answer = "Headaches can have many causes including stress, tension, dehydration, lack of sleep, eye strain, or underlying medical conditions. Common types include tension headaches, migraines, and cluster headaches. Rest, hydration, and over-the-counter pain relievers may help. See a doctor for severe, persistent, or worsening headaches."
                elif 'fever' in question_lower:
                    answer = "Fever is a temporary increase in body temperature, often due to an infection. Normal body temperature is around 98.6°F (37°C). A fever is generally considered to be 100.4°F (38°C) or higher. Rest, stay hydrated, and use fever reducers if needed. Seek medical attention for high fevers (above 103°F/39.4°C) or if fever lasts more than 3 days."
                else:
                    answer = self._get_fallback_response(question, language)
            else:
                # Tokenize inputs
                inputs = self.qa_tokenizer(
                    question,
                    context,
                    add_special_tokens=True,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512,
                    padding="max_length"
                ).to(self.device)
                
                # Get model predictions
                with torch.no_grad():
                    outputs = self.qa_model(**inputs)
                
                # Get start and end scores with some confidence threshold
                start_scores = torch.softmax(outputs.start_logits, dim=1)
                end_scores = torch.softmax(outputs.end_logits, dim=1)
                
                # Get the most likely answer span
                answer_start = torch.argmax(start_scores)
                answer_end = torch.argmax(end_scores) + 1
                
                # Calculate confidence score
                confidence = float((start_scores[0, answer_start] + end_scores[0, answer_end-1]) / 2)
                
                # Only use the model's answer if confidence is above threshold
                if confidence > 0.3:  # Adjust threshold as needed
                    answer_tokens = inputs.input_ids[0][answer_start:answer_end]
                    answer = self.qa_tokenizer.decode(answer_tokens, skip_special_tokens=True)
                else:
                    answer = await self._get_fallback_response(question, language)
            
            # If answer is still empty or too short, use fallback
            if not answer.strip() or len(answer.split()) < 3:
                answer = await self._get_fallback_response(question, language)
            
            # Translate if needed and Khaya is available
            if language == "ak" and self.translator:
                try:
                    answer = await self.translator.translate(text=answer, target_lang="ak")
                except Exception as e:
                    logger.warning(f"Translation failed: {str(e)}")
            
            return {
                "answer": answer,
                "language": language,
                "confidence": float(torch.max(torch.softmax(outputs.start_logits, dim=1))),
                "model": "BioBERT",
                "translated": language == "ak"
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}", exc_info=True)
            return {
                "answer": self._get_fallback_response(question, language),
                "language": language,
                "error": str(e)
            }
    
    async def _search_web_medical(self, question: str, language: str = 'en') -> Optional[str]:
        """Search trusted medical sources for an answer"""
        try:
            # Add site: filter for trusted domains
            site_filter = ' OR '.join(f'site:{domain}' for domain in TRUSTED_MEDICAL_DOMAINS)
            query = f"{question} {site_filter}"
            
            # Search using the web search tool
            search_results = await search_web(query=query, domain='')
            
            # Process results to find the most relevant snippet
            if search_results and 'organic_results' in search_results:
                for result in search_results['organic_results']:
                    # Skip non-medical domains
                    if not any(domain in result.get('link', '') for domain in TRUSTED_MEDICAL_DOMAINS):
                        continue
                        
                    # Get the most relevant snippet
                    snippet = result.get('snippet', '')
                    if snippet:
                        # Clean up the snippet
                        snippet = re.sub(r'\s+', ' ', snippet)  # Normalize whitespace
                        snippet = re.sub(r'\[\d+\]', '', snippet)  # Remove citation numbers
                        return f"According to {result.get('source', 'medical sources')}: {snippet}"
                        
        except Exception as e:
            logger.error(f"Error in web search: {str(e)}")
            
        return None

    async def _get_fallback_response(self, question: str, language: str) -> str:
        """Get a fallback response when the model can't generate an answer"""
        # First try to find an answer online
        try:
            web_answer = await self._search_web_medical(question, language)
            if web_answer:
                return web_answer
        except Exception as e:
            logger.warning(f"Web search failed: {str(e)}")
        
        # If web search fails, use the standard fallback
        fallbacks = {
            "en": "I couldn't find a specific answer to your medical question. For accurate medical advice, please consult with a healthcare professional.",
            "ak": "Mentumi annya nkyerɛaseɛ a ɛfa wo ho asɛm no ho. Sɛ wupɛ nkyerɛkyerɛ a ɛte saa a, yɛsrɛ wo kɔ nhwehwɛmufoɔ nkyɛn wɔ ayaresa mu."
        }
        return fallbacks.get(language, fallbacks["en"])
    
    async def translate_text(self, text: str, target_lang: str = "ak") -> str:
        """
        Translate text using fallback translation
        
        Args:
            text: Text to translate
            target_lang: Target language (default: "ak" for Akan)
            
        Returns:
            Translated text
        """
        if not text.strip() or target_lang != "ak":
            return text
            
        try:
            # Simple word-by-word translation for known terms
            translated_words = []
            for word in text.lower().split():
                if word in self.translation_dict:
                    translated_words.append(self.translation_dict[word])
                else:
                    translated_words.append(word)
            
            return " ".join(translated_words)
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text  # Return original text if translation fails
