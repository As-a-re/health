import json
import re
from difflib import get_close_matches
from typing import Dict, List, Optional, Union

class HealthQA:
    def __init__(self, knowledge_file: str):
        """Initialize the HealthQA with medical knowledge from a JSON file."""
        self.knowledge = self._load_knowledge(knowledge_file)
        self.disease_names = [disease['name'].lower() for disease in self.knowledge['diseases']]
        
        # Common responses in different languages
        self.responses = {
            'en': {
                'no_question': "Please ask a health-related question.",
                'unsure_condition': "I'm not sure which health condition you're asking about. Could you please be more specific?",
                'no_info': "I don't have information about {}. I can provide information about: {}",
                'about': "About {}:",
                'symptoms': "\nCommon symptoms include: {}",
                'treatments': "\nTreatment options include: {}",
                'causes': "\nPossible causes include: {}",
                'precautions': "\nPrecautions to take: {}",
                'risk_groups': "\nPeople at higher risk: {}",
                'transmission': "\nTransmission: {}",
                'disclaimer': "\n\nNote: This information is for educational purposes only and should not replace professional medical advice. Please consult a healthcare provider for medical advice."
            },
            'ak': {
                'no_question': "Yɛsrɛ wo, bisisa abakɔsɛm a ɛfa yareɛ ho.",
                'unsure_condition': "Mennim yareɛ a wubisa ho asɛm no mu dɛn. So wubetumi aka kyerɛ kɛse?",
                'no_info': "Minnim {0} ho asɛm. Metumi ama wo nimdeɛ fa {1} ho.",
                'about': "Nea ɛfa {} ho:",
                'symptoms': "\nYareɛ no nsɛnkyerɛnne ahorow ne: {}",
                'treatments': "\nYareɛ no ayaresa ne: {}",
                'causes': "\nEbetumi aba efise: {}",
                'precautions': "\nNneɛma a woyɛ: {}",
                'risk_groups': "\nNnipa a wɔwɔ yareɛ yi so yɛ: {}",
                'transmission': "\nƐnam saa kwan so na ɛnam so kɔ: {}",
                'disclaimer': "\n\nNkyerɛkyerɛ: Wɔde nsɛm yi ama w'ani nkɔ so nanso ɛnyɛ oduruyɛfoɔ adwuma. Yɛsrɛ wo kɔbisa oduruyɛfoɔ foforo."
            }
        }
        
        # Common medical terms in Akan for better matching
        self.akan_medical_terms = {
            'yareɛ': 'disease',
            'nsɛnkyerɛnne': 'symptoms',
            'ayaresa': 'treatments',
            'aduru': 'medicine',
            'yare': 'sickness',
            'aduru a wɔde sa': 'medicine',
            'aduru a ɛyɛ fɛ': 'treatment',
            'aduru a ɛyɛ fɛ ma': 'treatment for',
            'sɛn na ɛfa yareɛ': 'what is',
            'sɛn na ɛyɛ': 'what is',
            'sɛn na ɛma': 'what causes',
            'sɛn na ɛbɛma': 'what will make',
            'sɛn na ɛbɛyɛ a': 'what will happen if'
        }
        
    def _load_knowledge(self, file_path: str) -> Dict:
        """Load medical knowledge from a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Error: The file {file_path} was not found.")
            return {'diseases': []}
        except json.JSONDecodeError:
            print(f"Error: The file {file_path} is not a valid JSON file.")
            return {'diseases': []}
    
    def _find_disease(self, disease_name: str) -> Optional[Dict]:
        """Find a disease by name or synonym, with fuzzy matching."""
        disease_name = disease_name.lower()
        
        # First try exact match
        for disease in self.knowledge['diseases']:
            if disease['name'].lower() == disease_name:
                return disease
            if disease_name in [s.lower() for s in disease.get('synonyms', [])]:
                return disease
        
        # Try fuzzy matching if no exact match found
        matches = get_close_matches(disease_name, self.disease_names, n=1, cutoff=0.6)
        if matches:
            for disease in self.knowledge['diseases']:
                if disease['name'].lower() == matches[0]:
                    return disease
        
        return None
    
    def _format_list(self, items: List[str]) -> str:
        """Format a list of items as a comma-separated string."""
        if not items:
            return "No information available."
        return ", ".join(items)
    
    def _translate_query_to_english(self, query: str) -> str:
        """
        Translate common Akan medical terms to English for better matching.
        """
        query = query.lower()
        for akan, eng in self.akan_medical_terms.items():
            query = query.replace(akan.lower(), eng.lower())
        return query

    def _get_response_text(self, key: str, language: str, *args) -> str:
        """
        Get localized response text.
        Falls back to English if translation not available.
        """
        lang = language if language in self.responses else 'en'
        return self.responses[lang].get(key, self.responses['en'].get(key, '')).format(*args)

    def _extract_disease_and_question(self, question: str, language: str = "en") -> tuple:
        """
        Extract the disease name and question type from the user's question.
        """
        if language == 'ak':
            # First translate Akan medical terms to English for processing
            question = self._translate_query_to_english(question)
        
        question = question.lower().strip('? ')
        
        # Define question patterns and their corresponding answer types
        patterns = {
            'symptoms': r'(?:what (?:are|is) (?:the )?)?symptoms? (?:of|for) (.+)',
            'treatments': r'(?:what (?:are|is) (?:the )?)?treatments? (?:for|of) (.+)',
            'causes': r'(?:what (?:are|is) (?:the )?)?causes? (?:of|for) (.+)',
            'precautions': r'(?:what (?:are|is) (?:the )?)?precautions? (?:for|against) (.+)',
            'risk_groups': r'(?:who is at )?risk (?:for|of) (.+)',
            'type': r'(?:what (?:is|are) (?:the )?)?type (?:of )?(.+)',
            'transmission': r'how (?:is|are) (.+?) (?:transmitted|spread)',
            'info': r'(?:what (?:is|are)|tell me about) (.+)'
        }
        
        # Find matching pattern
        question_type = None
        disease_name = None
        
        for q_type, pattern in patterns.items():
            match = re.match(pattern, question, re.IGNORECASE)
            if match:
                question_type = q_type
                disease_name = match.group(1).strip()
                break
        
        # If no specific pattern matched, try to find a disease name in the question
        if not disease_name or not question_type:
            # Look for disease names in the question
            for disease in self.knowledge['diseases']:
                # Check disease name
                if disease['name'].lower() in question:
                    disease_name = disease['name'].lower()
                    break
                # Check synonyms
                for synonym in disease.get('synonyms', []):
                    if synonym.lower() in question:
                        disease_name = disease['name'].lower()
                        break
                if disease_name:
                    break
            
            # If we found a disease but no question type, assume they want general info
            if disease_name and not question_type:
                question_type = 'info'
        
        # If we still don't have a disease name, try to extract it by removing common question words
        if not disease_name:
            # Remove common question words and phrases
            common_phrases = [
                'what', 'are', 'is', 'the', 'of', 'for', 'symptoms', 'treatments',
                'causes', 'precautions', 'risk', 'how', 'transmitted', 'spread',
                'tell me about', 'information', 'about'
            ]
            words = [word for word in question.split() if word.lower() not in common_phrases]
            disease_name = ' '.join(words).strip()
        
        # Clean up the disease name
        if disease_name:
            disease_name = disease_name.strip('? ').strip()
        
        # If we have a question type but no disease name, try to extract it from the question
        if question_type and not disease_name:
            # Try to find the longest matching disease name in the question
            best_match = ''
            for disease in self.knowledge['diseases']:
                if disease['name'].lower() in question and len(disease['name']) > len(best_match):
                    best_match = disease['name'].lower()
                for synonym in disease.get('synonyms', []):
                    if synonym.lower() in question and len(synonym) > len(best_match):
                        best_match = disease['name'].lower()
            if best_match:
                disease_name = best_match
        
        return disease_name, question_type or 'info'
    
    def _get_translated_field(self, disease: dict, field: str, language: str) -> str:
        """
        Get a translated field from disease data, falling back to English.
        """
        # Check if there's a translation available for the requested language
        if language == 'ak' and 'translations' in disease and 'ak' in disease['translations']:
            return disease['translations']['ak'].get(field, disease.get(field, ""))
        return disease.get(field, "")

    def answer_question(self, question: str, language: str = "en") -> str:
        """
        Answer a health-related question based on the knowledge base.
        
        Args:
            question: The user's question
            language: Language code for the response ('en' or 'ak')
            
        Returns:
            str: The answer to the question in the requested language
        """
        if not question.strip():
            return self._get_response_text('no_question', language)
            
        # Extract disease and question type from the user's question
        disease_name, question_type = self._extract_disease_and_question(question, language)
        
        if not disease_name:
            return self._get_response_text('unsure_condition', language)
            
        # Find the disease in the knowledge base
        disease = self._find_disease(disease_name)
        
        if not disease:
            sample_diseases = ', '.join(self.disease_names[:3])
            return self._get_response_text('no_info', language, disease_name, sample_diseases)
        
        # Generate response based on question type
        response_parts = []
        
        # Get disease name in requested language
        disease_name_translated = self._get_translated_field(disease, 'name', language)
        response_parts.append(self._get_response_text('about', language, disease_name_translated))
        
        # Handle different question types
        if question_type == 'symptoms' and 'symptoms' in disease:
            symptoms = self._get_translated_field(disease, 'symptoms', language)
            response_parts.append(self._get_response_text('symptoms', language, self._format_list(symptoms)))
        
        elif question_type == 'treatments' and 'treatments' in disease:
            treatments = self._get_translated_field(disease, 'treatments', language)
            response_parts.append(self._get_response_text('treatments', language, self._format_list(treatments)))
        
        elif question_type == 'causes' and 'causes' in disease:
            causes = self._get_translated_field(disease, 'causes', language)
            response_parts.append(self._get_response_text('causes', language, self._format_list(causes)))
        
        elif question_type == 'precautions' and 'precautions' in disease:
            precautions = self._get_translated_field(disease, 'precautions', language)
            response_parts.append(self._get_response_text('precautions', language, self._format_list(precautions)))
        
        elif question_type == 'risk_groups' and 'risk_groups' in disease:
            risk_groups = self._get_translated_field(disease, 'risk_groups', language)
            response_parts.append(self._get_response_text('risk_groups', language, self._format_list(risk_groups)))
        
        elif question_type == 'transmission' and 'transmission' in disease:
            transmission = self._get_translated_field(disease, 'transmission', language)
            response_parts.append(self._get_response_text('transmission', language, transmission))
        
        # Default response with all available information
        else:
            # Description
            description = self._get_translated_field(disease, 'description', language)
            if description:
                response_parts.append(f"\n{description}")
            
            # Symptoms
            if 'symptoms' in disease:
                symptoms = self._get_translated_field(disease, 'symptoms', language)
                response_parts.append(self._get_response_text('symptoms', language, self._format_list(symptoms)))
            
            # Treatments
            if 'treatments' in disease:
                treatments = self._get_translated_field(disease, 'treatments', language)
                response_parts.append(self._get_response_text('treatments', language, self._format_list(treatments)))
            
            # Precautions
            if 'precautions' in disease:
                precautions = self._get_translated_field(disease, 'precautions', language)
                response_parts.append(self._get_response_text('precautions', language, self._format_list(precautions)))
        
        # Add a disclaimer
        response_parts.append(self._get_response_text('disclaimer', language))
        
        return "".join(response_parts)

def main():
    # Initialize the HealthQA system
    qa = HealthQA('medical_knowledge.json')
    
    print("Health Information System")
    print("Type 'quit' to exit")
    print("You can ask questions like:")
    print("- What are the symptoms of malaria?")
    print("- What are the treatments for diabetes?")
    print("- How is COVID-19 transmitted?")
    print("- Who is at risk for tuberculosis?")
    print()
    
    while True:
        question = input("\nYour question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
            
        if not question:
            continue
            
        answer = qa.answer_question(question)
        print("\n" + answer + "\n")

if __name__ == "__main__":
    main()
