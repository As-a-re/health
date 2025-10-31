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
            # General terms
            'yareɛ': 'disease',
            'yare': 'sickness',
            'aduru': 'medicine',
            'nsɛnkyerɛnne': 'symptoms',
            'ayaresa': 'treatments',
            'mfitiaseɛ': 'causes',
            'nsa ho nhyehyɛeɛ': 'precautions',
            'nnipa a wɔwɔ kwan so': 'risk groups',
            'kwan a ɛfa so kɔ': 'transmission',
            
            # Common disease names
            'kɔlera': 'cholera',
            'kolerae': 'cholera',
            'kɔlɛra': 'cholera',
            'kɔlɛrɛ': 'cholera',
            'kɔlɛla': 'cholera',
            'atiridii': 'malaria',
            'atiridi': 'malaria',
            'atiridi yare': 'malaria',
            'asraafo': 'influenza',
            'asrafo': 'influenza',
            'asra': 'fever',
            'asraa': 'fever',
            'mogya yare': 'hypertension',
            'mogyayare': 'hypertension',
            'sukaduru yare': 'diabetes',
            'sukaduruyare': 'diabetes',
            'asamando yare': 'tuberculosis',
            'asamandoyare': 'tuberculosis',
            'nsuo aserew': 'diarrhea',
            'nsu aserew': 'diarrhea',
            'nsuonserew': 'diarrhea',
            'nsuonserew': 'diarrhea',
            'koronayare': 'covid-19',
            'koronayareɛ': 'covid-19',
            'covid': 'covid-19',
            'covid-19': 'covid-19',
            'covid 19': 'covid-19',
            'sars-cov-2': 'covid-19',
            
            # Question phrases
            'deɛn na ɛma': 'what causes',
            'deɛn na ɛyɛ nti na': 'why does',
            'sɛn na ɛyɛ': 'what is',
            'sɛn na ɛma': 'what causes',
            'sɛn na ɛbɛma': 'what will cause',
            'sɛn na ɛfa': 'what is about',
            'deɛn na wɔde sa': 'what is used to treat',
            'deɛn na ɛyɛ fɛ ma': 'what is good for',
            'woyɛ deɛn ma': 'what do you do for',
            'wofa kwan bɛn so so': 'how do you prevent',
            
            # Common misspellings and variations
            'kɔlɛra': 'cholera',
            'kɔlɛla': 'cholera',
            'kɔlɛrɛ': 'cholera',
            'atiridi': 'malaria',
            'atiridi yare': 'malaria',
            'asrafo': 'influenza',
            'asraa': 'fever',
            'mogyayare': 'hypertension',
            'sukaduruyare': 'diabetes',
            'asamandoyare': 'tuberculosis',
            'nsuonserew': 'diarrhea',
            'nsuonserew': 'diarrhea',
            'nsuo aserew': 'diarrhea',
            'nsu aserew': 'diarrhea'
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
    
    def _find_disease(self, disease_name: str, language: str = 'en') -> Optional[Dict]:
        """
        Find a disease by name or synonym, with fuzzy matching.
        Checks both English and Akan names/translations.
        """
        disease_name = disease_name.lower().strip()
        
        for disease in self.knowledge['diseases']:
            # Check English name and synonyms
            if disease_name == disease['name'].lower():
                return disease
                
            if disease_name in [s.lower() for s in disease.get('synonyms', [])]:
                return disease
            
            # Check Akan translations if available
            if 'translations' in disease and 'ak' in disease['translations']:
                ak_trans = disease['translations']['ak']
                # Check Akan name
                if disease_name == ak_trans.get('name', '').lower():
                    return disease
                # Check Akan synonyms
                if 'synonyms' in ak_trans and disease_name in [s.lower() for s in ak_trans['synonyms']]:
                    return disease
        
        # If no exact match, try fuzzy matching on English names
        matches = get_close_matches(disease_name, self.disease_names, n=1, cutoff=0.6)
        if matches:
            for disease in self.knowledge['diseases']:
                if disease['name'].lower() == matches[0]:
                    return disease
        
        # If still no match, try fuzzy matching on Akan names
        akan_disease_names = []
        for disease in self.knowledge['diseases']:
            if 'translations' in disease and 'ak' in disease['translations']:
                ak_trans = disease['translations']['ak']
                akan_disease_names.append(ak_trans.get('name', '').lower())
                akan_disease_names.extend([s.lower() for s in ak_trans.get('synonyms', [])])
        
        if akan_disease_names:
            matches = get_close_matches(disease_name, akan_disease_names, n=1, cutoff=0.6)
            if matches:
                # Find the disease that matches the Akan name
                for disease in self.knowledge['diseases']:
                    if 'translations' in disease and 'ak' in disease['translations']:
                        ak_trans = disease['translations']['ak']
                        if (matches[0] == ak_trans.get('name', '').lower() or 
                            matches[0] in [s.lower() for s in ak_trans.get('synonyms', [])]):
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
        Handles disease names, symptoms, and common medical terms.
        """
        # Make a copy of the query to modify
        translated = query.lower()
        
        # First, try to find and translate disease names (longer phrases first)
        disease_terms = sorted(
            [(k, v) for k, v in self.akan_medical_terms.items() if ' ' in k],
            key=lambda x: len(x[0]),
            reverse=True
        )
        
        # Replace longer phrases first to avoid partial matches
        for akan, eng in disease_terms:
            if akan in translated:
                translated = translated.replace(akan, eng)
        
        # Then replace individual words
        for akan, eng in self.akan_medical_terms.items():
            if ' ' not in akan:  # Only single words here
                # Use word boundaries to avoid partial matches
                translated = re.sub(r'\b' + re.escape(akan) + r'\b', eng, translated)
        
        # Handle common question patterns
        patterns = {
            r'deɛn na yɛbɛyɛ a yɛbɛsiw': 'how to prevent',
            r'deɛn na yɛbɛyɛ a yɛbɛsiw so': 'how to prevent',
            r'yareɛ no nsɛnkyerɛnne ahorow ne': 'symptoms of',
            r'yareɛ no ayaresa ne': 'treatments for',
            r'nnipa a wɔwɔ yareɛ yi so yɛ': 'risk groups for',
            r'deɛn na ɛyɛ nti na': 'what causes',
            r'deɛn na ɛma': 'what causes',
            r'sɛn na ɛyɛ': 'what is',
            r'deɛn na wɔde sa': 'how to treat',
            r'deɛn na ɛyɛ fɛ ma': 'what is good for',
            r'woyɛ deɛn ma': 'what to do for',
            r'wofa kwan bɛn so so': 'how to prevent'
        }
        
        for pattern, replacement in patterns.items():
            translated = re.sub(pattern, replacement, translated, flags=re.IGNORECASE)
        
        return translated.strip()

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
        original_question = question.lower().strip('? ')
        
        # Define Akan question patterns
        akan_patterns = {
            'symptoms': [
                # Patterns for asking about symptoms
                r'(?:nsɛnkyerɛnne|nsɛnkyerɛnne ahorow|nsɛnkyerɛnne a ɛwɔ|nsɛnkyerɛnne ahorow a ɛwɔ) (?:a ɛwɔ )?(.+)',
                r'(?:deɛn ne )?(.+) (nsɛnkyerɛnne|nsɛnkyerɛnne ahorow)',
                r'(.+) (nsɛnkyerɛnne|nsɛnkyerɛnne ahorow) (deɛn|ne deɛn)',
                r'(.+) no (nsɛnkyerɛnne|nsɛnkyerɛnne ahorow) deɛn',
                r'(.+) no (nsɛnkyerɛnne|nsɛnkyerɛnne ahorow) ne deɛn',
                r'(.+) no (nsɛnkyerɛnne|nsɛnkyerɛnne ahorow) ye deɛn',
                r'(.+) no (nsɛnkyerɛnne|nsɛnkyerɛnne ahorow) ye deɛn?',
                r'(.+) no (nsɛnkyerɛnne|nsɛnkyerɛnne ahorow) deɛn?'
            ],
            'treatments': [
                # Patterns for asking about treatments
                r'(?:ayaresa|aduru a wɔde sa|aduruyɛ|ayaresa ahorow|aduru ahorow a wɔde sa) (?:a ɛwɔ hɔ ma|ma|a ɛsa|a ɛyɛ fɛ de sa) (.+)',
                r'(?:deɛn na wɔde sa|deɛn na ɛyɛ ayaresa ma|deɛn na yɛde sa|deɛn na ɛfata ayaresa ma|deɛn na ɛyɛ mfaso ma) (.+)',
                r'(?:deɛn na wɔde sa|ayaresa|aduruyɛ) (a ɛwɔ hɔ ma|ma|a ɛsa) (.+)',
                r'(.+) (ayaresa|aduru a wɔde sa|aduruyɛ|ayaresa ahorow|aduru ahorow a wɔde sa) (deɛn|ne deɛn|ye deɛn|yɛ deɛn|deɛn na ɛyɛ fɛ ma|deɛn na ɛfata ma)',
                r'(.+) no (ayaresa|aduru a wɔde sa|aduruyɛ|ayaresa ahorow) (deɛn|ne deɛn|ye deɛn|yɛ deɛn|deɛn na ɛyɛ fɛ ma|deɛn na ɛfata ma)',
                r'(.+) no (ayaresa|aduru a wɔde sa|aduruyɛ) (deɛn|ne deɛn|ye deɛn|yɛ deɛn|deɛn na ɛyɛ fɛ ma|deɛn na ɛfata ma)\?',
                r'(yɛ deɛn ayaresa|yɛ deɛn aduruyɛ|yɛ deɛn aduru a wɔde sa) (a ɛwɔ hɔ ma|ma|a ɛsa) (.+)',
                r'(yɛ deɛn ayaresa|yɛ deɛn aduruyɛ) (a ɛwɔ hɔ ma|ma|a ɛsa) (.+) (mu|ho|no|mu no|ho no|mu yi|ho yi)',
                r'(.+) (ayaresa|aduruyɛ) (a wɔde sa|a wɔde yɛ ma|a ɛyɛ fɛ yɛ ma|a ɛfata yɛ ma|a ɛyɛ mfaso ma)',
                r'(.+) (ayaresa|aduruyɛ) (a ɛfata|a ɛfata ma|a ɛyɛ mfaso ma|a ɛyɛ fɛ ma)',
                r'(.:wofa deɛn sa|wofa deɛn yɛ ma|wɔfa deɛn sa|wɔfa deɛn yɛ ma|yɛfa deɛn sa|yɛfa deɛn yɛ ma) (.+)',
                r'(.:woyɛ deɛn ma|wosa deɛn ma|wɔyɛ deɛn ma|wɔsa deɛn ma|yɛyɛ deɛn ma|yɛsa deɛn ma) (.+)',
                r'(.+) (ayaresa|aduruyɛ) (a ɛte sɛn|a ɛte dɛn|a ɛyɛ te sɛn|a ɛyɛ te dɛn)',
                r'(.:deɛn na wɔde sa|ayaresa|aduruyɛ) (a ɛwɔ hɔ ma|ma|a ɛsa) (.+) (yare|yareɛ|yare a ɛwɔ|yareɛ a ɛwɔ|yare no|yareɛ no)',
                r'(.:deɛn na wɔde sa|ayaresa|aduruyɛ) (a ɛwɔ hɔ ma|ma|a ɛsa) (.+) (mu|ho|no|mu no|ho no|mu yi|ho yi|mu no mu|ho no mu)'
            ],
            'risk_groups': [
                # Patterns for asking about risk groups
                r'(?:hwan|nnafoɔ|nnipa ahe|nnipa bɛn) (?:na ɛtumi nya|a wɔtumi nya|a wɔwɔ|a wɔwɔ ho kɛseɛ|a wɔwɔ ho kɛseɛ ma) (.+)',
                r'(.+) (hwan|nnafoɔ|nnipa ahe|nnipa bɛn) (na ɛtumi nya|a wɔtumi nya|a wɔwɔ|a wɔwɔ ho kɛseɛ|a wɔwɔ ho kɛseɛ ma)',
                r'(hwan|nnafoɔ|nnipa ahe|nnipa bɛn) na ɛtumi nya (.+)',
                r'(.+) no (hwan|nnafoɔ|nnipa ahe|nnipa bɛn) na ɛtumi nya',
                r'(hwan|nnafoɔ|nnipa ahe|nnipa bɛn) na wɔtumi nya (.+)',
                r'(.+) no (hwan|nnafoɔ|nnipa ahe|nnipa bɛn) na wɔtumi nya',
                r'(hwan|nnafoɔ|nnipa ahe|nnipa bɛn) na ɛwɔ (.+) ho kɛseɛ',
                r'(.+) no (hwan|nnafoɔ|nnipa ahe|nnipa bɛn) na ɛwɔ ho kɛseɛ'
            ],
            'causes': [
                # Patterns for asking about causes
                r'(?:deɛn na ɛma|deɛn na ɛyɛ nti na|deɛn nti na) (.+) (ba|baa|baeɛ|baa hɔ)',
                r'(.+) (baeɛ|baa|baa hɔ) efisɛ deɛn',
                r'(.+) (mfitiaseɛ|mfitiase|mfitiaseɛ a ɛyɛ nti|mfitiase a ɛyɛ nti) deɛn',
                r'(.+) no (mfiaseɛ|mfiase|mfitiaseɛ|mfitiase) deɛn',
                r'(.+) no (mfiaseɛ|mfiase|mfitiaseɛ|mfitiase) ne deɛn',
                r'(.+) no (mfiaseɛ|mfiase|mfitiaseɛ|mfitiase) ye deɛn',
                r'(deɛn na ɛyɛ nti na) (.+) ba',
                r'(deɛn na ɛma) (.+) baeɛ'
            ],
            'precautions': [
                # Patterns for asking about precautions
                r'(.:deɛn na yɛbɛyɛ a yɛnsiw|deɛn na yɛbɛyɛ a yɛbɛsiw|deɛn na yɛbɛyɛ a yɛbɛsiw so) (.+)',
                r'(.+) (nsiw ho nneɛma|nsie ho nneɛma|nneɛma a ɛsɛ sɛ yɛyɛ) deɛn',
                r'(.+) no (nsiw ho nneɛma|nsie ho nneɛma|nneɛma a ɛsɛ sɛ yɛyɛ) ne deɛn',
                r'(.+) no (nsa ho nhyehyɛeɛ|nsa ho nhyehyɛe) deɛn',
                r'(.:deɛn na ɛsɛ sɛ yɛyɛ ma) (.+) nnyɛ ha',
                r'(.:deɛn na ɛsɛ sɛ yɛyɛ sɛ yɛnnyɛ) (.+)',
                r'(.+) (nsa ho nhyehyɛeɛ|nsa ho nhyehyɛe) deɛn',
                r'(.:yɛ deɛn na ɛsɛ sɛ yɛyɛ ma yɛnnyɛ) (.+)'
            ],
            'transmission': [
                # Patterns for asking about transmission
                r'(.:deɛn na ɛfa kwan so na ɛnam so kɔ|deɛn na ɛfa kwan so na ɛnam so kɔ ma) (.+)',
                r'(.+) (nam kwan bɛn so na ɛnam so kɔ|nam kwan bɛn so na ɛfa so kɔ)',
                r'(.:deɛn na ɛma) (.+) (nam so kɔ|fa so kɔ)',
                r'(.+) (nam kwan bɛn so na ɛnam so kɔ|nam kwan bɛn so na ɛfa so kɔ)',
                r'(.+) no (nam kwan bɛn so na ɛnam so kɔ|nam kwan bɛn so na ɛfa so kɔ)',
                r'(.:deɛn na ɛma) (.+) (nam so kɔ|fa so kɔ)',
                r'(.+) (nam kwan bɛn so na ɛnam so kɔ|nam kwan bɛn so na ɛfa so kɔ)',
                r'(.+) no (nam kwan bɛn so na ɛnam so kɔ|nam kwan bɛn so na ɛfa so kɔ)'
            ],
            'info': [
                # General information patterns
                r'ka kyere me ho asɛm fa (.+) ho',
                r'(.+) ho nsɛm',
                r'deɛn ne (.+)',
                r'(.+) deɛn',
                r'ka kyere me ho asɛm fa (.+)',
                r'(.+) ho asɛm deɛn',
                r'(.+) ho nsɛm deɛn',
                r'(.+) ho asɛm'
            ]
        }
        
        # Define English question patterns with comprehensive matching
        english_patterns = {
            'symptoms': [
                # Patterns for asking about symptoms
                r'(?:what (?:are|is|would be|might be|could be) (?:the )?)?(?:signs|symptoms|symptom|sign) (?:of|for|with) (.+)',
                r'(?:what (?:do|does) (.+) (?:feel like|look like|show|present))',
                r'(?:how (?:do|does) (?:you|one) (?:know|tell) if (?:you|someone) (?:has|have|got) (.+))',
                r'(.+) (?:symptoms|symptom|signs|sign)(?: of)?(?: the disease| this condition)?(?: look like| feel like)?',
                r'(?:what (?:are|is) (?:the )?(?:main |common |most common )?(?:symptoms|symptom|signs|sign) (?:of|for) (.+))',
                r'(?:what (?:are|is) (?:the )?(?:main |common |most common )?(.+) (?:symptoms|symptom|signs|sign))',
                r'(?:how (?:do|does) (?:you|one) (?:recognize|identify) (.+))',
                r'(?:what (?:are|is) (?:the )?indications (?:of|for) (.+))',
                r'(?:what (?:are|is) (?:the )?warning signs (?:of|for) (.+))',
                r'(?:what (?:are|is) (?:the )?clinical manifestations (?:of|for) (.+))'
            ],
            'treatments': [
                # Patterns for asking about treatments
                r'(?:what (?:are|is) (?:the )?(?:possible |available |common )?(?:treatments|treatment|remedies|remedy) (?:for|of) (.+))',
                r'(?:how (?:do|does|can) (.+) (?:treat|be treated|be managed|be cured))',
                r'(?:what (?:is|are) (?:the )?(?:best |most effective )?(?:treatments|treatment|remedies|remedy) (?:for|of) (.+))',
                r'(?:how (?:do|does) (?:you|doctors|physicians) (?:treat|manage|cure) (.+))',
                r'(.+) (?:treatments|treatment|remedies|remedy)(?: options)?(?: available)?(?: for this condition)?',
                r'(?:what (?:are|is) (?:the )?treatment options (?:for|of) (.+))',
                r'(?:how (?:can|do) (?:you|one) (?:treat|manage|cure) (.+))',
                r'(?:what (?:are|is) (?:the )?management options (?:for|of) (.+))',
                r'(?:what (?:are|is) (?:the )?therapies (?:for|of) (.+))',
                r'(?:what (?:are|is) (?:the )?medications (?:for|of|used for) (.+))'
            ],
            'causes': [
                # Patterns for asking about causes
                r'(?:what (?:are|is) (?:the )?(?:main |common |primary |possible )?causes? (?:of|for) (.+))',
                r'(?:what (?:causes?|triggers?|leads to|results in|brings on) (.+))',
                r'(?:how (?:do|does) (?:you|one) (?:get|develop|contract) (.+))',
                r'(?:why (?:do|does) (?:people|you|one) (?:get|develop|have) (.+))',
                r'(?:what (?:are|is) (?:the )?risk factors (?:for|of) (.+))',
                r'(.+) (?:causes?|reasons?|origins?|sources?)(?: of)?(?: the disease| this condition)?',
                r'(?:what (?:are|is) (?:the )?underlying (?:reasons|factors) (?:for|of) (.+))',
                r'(?:how (?:do|does) (?:you|one) (?:end up with|come down with) (.+))',
                r'(?:what (?:are|is) (?:the )?etiology (?:of|for) (.+))',
                r'(?:what (?:are|is) (?:the )?pathogenesis (?:of|for) (.+))'
            ],
            'precautions': [
                # Patterns for asking about precautions
                r'(?:what (?:are|is) (?:the )?(?:safety |health |preventive )?precautions? (?:for|against|with) (.+))',
                r'(?:how (?:can|do) (?:you|one) (?:prevent|avoid|stop) (.+))',
                r'(?:what (?:are|is) (?:the )?preventive measures (?:for|against) (.+))',
                r'(?:how (?:can|do) (?:you|one) (?:protect|safeguard) (?:yourself|oneself) (?:from|against) (.+))',
                r'(?:what (?:are|is) (?:the )?(?:safety|health) measures (?:for|against) (.+))',
                r'(?:how (?:can|do) (?:you|one) (?:reduce|lower) (?:the )?risk (?:of|for) (.+))',
                r'(?:what (?:are|is) (?:the )?dos and don\'ts (?:for|with) (.+))',
                r'(?:how (?:can|do) (?:you|one) (?:minimize|lessen) (?:the )?chances (?:of|for) (.+))',
                r'(?:what (?:are|is) (?:the )?safety tips (?:for|with) (.+))',
                r'(?:how (?:can|do) (?:you|one) (?:stay safe|protect yourself) (?:from|against) (.+))'
            ],
            'risk_groups': [
                # Patterns for asking about risk groups
                r'(?:who|what kind of people|which people|what groups) (?:is|are|can get|might get|are at risk (?:for|of)) (.+)',
                r'(?:who is|who are|who can be) (?:at )?(?:high |greater |increased |elevated )?risk (?:for|of) (.+)',
                r'(?:who is|who are) (?:most )?(?:likely to (?:get|develop|contract)|vulnerable to|susceptible to|prone to) (.+)',
                r'who (?:can|might|may) (?:get|develop|contract) (.+)',
                r'who (?:is|are) (?:most )?(?:affected by|impacted by|troubled by) (.+)',
                r'who (?:is|are) (?:most )?(?:at (?:high )?risk (?:for|of)|vulnerable to) (.+)',
                r'(?:which|what) (?:group|groups|population|populations|demographic|demographics) (?:is|are) (?:at risk for|vulnerable to) (.+)',
                r'(?:who|what people) (?:is|are) (?:most )?likely to (?:develop|get|contract) (.+)',
                r'who (?:is|are) (?:most )?susceptible to (?:getting|developing|contracting) (.+)',
                r'who (?:is|are) (?:most )?in danger of (?:getting|developing|contracting) (.+)',
                r'who (?:is|are) (?:most )?prone to (?:getting|developing|contracting) (.+)',
                r'who (?:is|are) (?:most )?vulnerable to (?:getting|developing|contracting) (.+)',
                r'who (?:is|are) (?:most )?at risk of (?:getting|developing|contracting) (.+)',
                r'who (?:is|are) (?:most )?at risk for (?:getting|developing|contracting) (.+)'
            ],
            'transmission': [
                # Patterns for asking about transmission
                r'how (?:is|are) (.+?) (?:transmitted|spread|contracted|passed on|transferred|communicated)',
                r'how (?:does|do) (.+?) (?:spread|transmit|pass from person to person|get transmitted)',
                r'(?:what (?:is|are) (?:the )?(?:modes? of )?transmission (?:of|for) (.+))',
                r'(?:how (?:can|do) (?:you|one) (?:get|catch|contract) (.+))',
                r'(?:what (?:is|are) (?:the )?ways (?:that|in which) (.+) (?:is|are) (?:spread|transmitted))',
                r'(?:how (?:does|do) (?:people|one) (?:get|catch|contract) (.+))',
                r'(?:what (?:is|are) (?:the )?routes (?:of )?(?:transmission|infection) (?:for|of) (.+))',
                r'(?:how (?:is|are) (.+) (?:passed|transmitted) (?:from person to person|between people))',
                r'(?:what (?:is|are) (?:the )?means (?:of )?(?:transmission|spread) (?:for|of) (.+))',
                r'(?:how (?:can|do) (.+) (?:be|get) (?:transmitted|spread|passed on))'
            ],
            'info': [
                # General information patterns
                r'(?:what (?:are|is|do you know about) (.+))',
                r'(?:tell me (?:all|something|more) about (.+))',
                r'(?:give me (?:some )?information (?:about|on) (.+))',
                r'(?:what can you tell me about (.+))',
                r'(?:explain (?:to me )?(?:about )?(.+))',
                r'(?:describe (?:to me )?(?:about )?(.+))',
                r'(?:i(?:\')?d like to know (?:more )?about (.+))',
                r'(?:i need (?:some )?information (?:about|on) (.+))',
                r'(?:can you (?:tell|explain|describe) (?:to me )?(?:about )?(.+))',
                r'(?:i want to know (?:more )?about (.+))',
                r'(?:what (?:do you know|can you tell me) about (.+))',
                r'(?:enlighten me (?:about|on) (.+))',
                r'(?:teach me (?:about|something about) (.+))',
                r'(?:i(?:\')?m interested in (?:learning|knowing) (?:more )?about (.+))',
                r'(?:i(?:\')?d like to learn (?:more )?about (.+))',
                r'(?:can you provide (?:me with )?(?:some )?information (?:about|on) (.+))',
                r'(?:i need to know (?:more )?about (.+))',
                r'(?:i(?:\')?m looking for information (?:about|on) (.+))',
                r'(?:what (?:is|are) (?:the )?facts (?:about|on) (.+))',
                r'(?:what (?:is|are) (?:the )?details (?:about|on) (.+))'
            ]
        }
        
        # Use the appropriate patterns based on language
        patterns = akan_patterns if language == 'ak' else english_patterns
        
        # If Akan, first try direct matching with Akan patterns
        if language == 'ak':
            question = original_question
        else:
            question = self._translate_query_to_english(original_question)
        
        # Find matching pattern
        question_type = None
        disease_name = None
        
        for q_type, pattern_list in patterns.items():
            # Handle both single pattern and list of patterns
            patterns_to_check = pattern_list if isinstance(pattern_list, list) else [pattern_list]
            
            for pattern in patterns_to_check:
                match = re.match(pattern, question, re.IGNORECASE)
                if match:
                    question_type = q_type
                    # The disease name is in the last group of the match
                    disease_name = match.group(match.lastindex).strip()
                    break
            if disease_name:  # Stop checking other patterns if we found a match
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
            
        # Find the disease in the knowledge base (case-insensitive search)
        disease = None
        for d in self.knowledge['diseases']:
            if d['name'].lower() == disease_name.lower():
                disease = d
                break
            # Check synonyms
            for synonym in d.get('synonyms', []):
                if synonym.lower() == disease_name.lower():
                    disease = d
                    break
            if disease:
                break
        
        # If still not found, try fuzzy matching
        if not disease:
            matches = get_close_matches(disease_name.lower(), 
                                     [d['name'].lower() for d in self.knowledge['diseases']], 
                                     n=1, 
                                     cutoff=0.6)
            if matches:
                disease = next((d for d in self.knowledge['diseases'] 
                              if d['name'].lower() == matches[0]), None)
        
        if not disease:
            sample_diseases = ', '.join(self.disease_names[:3])
            return self._get_response_text('no_info', language, disease_name, sample_diseases)
        
        # Generate response based on question type
        response_parts = []
        
        # Get disease name in requested language
        disease_name_translated = self._get_translated_field(disease, 'name', language)
        
        # Handle different question types
        if question_type == 'symptoms' and 'symptoms' in disease:
            symptoms = self._get_translated_field(disease, 'symptoms', language)
            if not symptoms:
                symptoms = self._get_translated_field(disease, 'symptoms', 'en')  # Fallback to English
            response_parts.append(self._get_response_text('symptoms', language, self._format_list(symptoms)))
        
        elif question_type == 'treatments' and 'treatments' in disease:
            treatments = self._get_translated_field(disease, 'treatments', language)
            if not treatments and 'treatment' in disease:  # Handle singular 'treatment' key
                treatments = self._get_translated_field(disease, 'treatment', language)
            if not treatments:  # Fallback to English
                treatments = disease.get('treatments', disease.get('treatment', []))
            response_parts.append(self._get_response_text('treatments', language, self._format_list(treatments)))
        
        elif question_type == 'causes' and 'causes' in disease:
            causes = self._get_translated_field(disease, 'causes', language)
            if not causes:  # Fallback to English
                causes = disease.get('causes', [])
            response_parts.append(self._get_response_text('causes', language, self._format_list(causes)))
        
        elif question_type == 'precautions' and 'precautions' in disease:
            precautions = self._get_translated_field(disease, 'precautions', language)
            if not precautions:  # Fallback to English
                precautions = disease.get('precautions', [])
            response_parts.append(self._get_response_text('precautions', language, self._format_list(precautions)))
        
        elif question_type == 'risk_groups' and 'risk_groups' in disease:
            risk_groups = self._get_translated_field(disease, 'risk_groups', language)
            if not risk_groups:  # Fallback to English
                risk_groups = disease.get('risk_groups', [])
            if risk_groups:  # Only add if we have risk groups
                response_parts.append(self._get_response_text('risk_groups', language, self._format_list(risk_groups)))
            else:
                # If no risk groups found, provide a generic response
                response_parts.append(self._get_response_text('no_info', language, "risk groups for " + disease_name_translated, ""))
        
        elif question_type == 'transmission' and 'transmission' in disease:
            transmission = self._get_translated_field(disease, 'transmission', language)
            if not transmission:  # Fallback to English
                transmission = disease.get('transmission', '')
            if transmission:
                response_parts.append(self._get_response_text('transmission', language, transmission))
        
        # If no specific information was found for the question type, provide general info
        if len(response_parts) == 0 or (len(response_parts) == 1 and response_parts[0].startswith("About")):
            # Add description if available
            description = self._get_translated_field(disease, 'description', language)
            if description:
                response_parts.append(f"\n{description}")
            
            # Add symptoms if available
            if 'symptoms' in disease and question_type != 'symptoms':
                symptoms = self._get_translated_field(disease, 'symptoms', language)
                if symptoms:
                    response_parts.append(self._get_response_text('symptoms', language, self._format_list(symptoms)))
            
            # Add treatments if available
            if ('treatments' in disease or 'treatment' in disease) and question_type != 'treatments':
                treatments = self._get_translated_field(disease, 'treatments', language) or \
                           self._get_translated_field(disease, 'treatment', language)
                if treatments:
                    response_parts.append(self._get_response_text('treatments', language, self._format_list(treatments)))
            
            # Add risk groups if available and not already added
            if 'risk_groups' in disease and question_type != 'risk_groups':
                risk_groups = self._get_translated_field(disease, 'risk_groups', language)
                if risk_groups:
                    response_parts.append(self._get_response_text('risk_groups', language, self._format_list(risk_groups)))
        
        # If we still don't have any content, say we don't have specific information
        if len(response_parts) == 0 or (len(response_parts) == 1 and response_parts[0].startswith("About")):
            return self._get_response_text('no_info', language, 
                                         f"{disease_name_translated} ({question_type})", 
                                         "symptoms, causes, treatments, or risk groups")
        
        # Add a disclaimer
        response_parts.append(self._get_response_text('disclaimer', language))
        
        # Ensure the response is properly formatted
        response = "".join(response_parts).strip()
        if not response:
            return self._get_response_text('no_info', language, disease_name_translated, "")
            
        return response

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
