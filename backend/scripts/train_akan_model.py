#!/usr/bin/env python3
"""
Script to fine-tune a medical AI model for Akan language support
This would typically use datasets like AfriMed-QA and Masakhane
"""

import os
import torch
from transformers import (
    AutoTokenizer, AutoModelForQuestionAnswering,
    TrainingArguments, Trainer, DataCollatorWithPadding
)
from datasets import Dataset, load_dataset
import pandas as pd
from typing import Dict, List
import json
import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

class AkanMedicalModelTrainer:
    def __init__(self, base_model: str = "bert-base-multilingual-cased"):
        self.base_model = base_model
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_base_model(self):
        """Load the base multilingual model"""
        print(f"Loading base model: {self.base_model}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model)
        self.model = AutoModelForQuestionAnswering.from_pretrained(self.base_model)
        
        print(f"Model loaded on device: {self.device}")
        
    def tokenize_function(self, examples):
        """Tokenize the examples for training"""
        # Tokenize both the questions and contexts together
        tokenized = self.tokenizer(
            examples["question" if "question" in examples else "questions"],
            examples["context" if "context" in examples else "contexts"],
            truncation="only_second",
            max_length=384,
            stride=128,
            return_overflowing_tokens=True,
            return_offsets_mapping=True,
            padding="max_length"
        )
        
        # Since one example might give us several features, we need a map from a feature to
        # its corresponding example. This key gives us just that.
        sample_mapping = tokenized.pop("overflow_to_sample_mapping")
        offset_mapping = tokenized.pop("offset_mapping")
        
        # Let's label those examples!
        tokenized["start_positions"] = []
        tokenized["end_positions"] = []
        
        for i, offsets in enumerate(offset_mapping):
            # We will label impossible answers with the index of the CLS token.
            input_ids = tokenized["input_ids"][i]
            cls_index = input_ids.index(self.tokenizer.cls_token_id)
            
            # Grab the sequence corresponding to that example (to know what is the context and what is the question).
            sequence_ids = tokenized.sequence_ids(i)
            
            # One example can give several spans, this is the index of the example containing this span of text.
            sample_index = sample_mapping[i]
            answers = self.examples[sample_index]["answers"]
            
            # If no answers are given, set the cls_index as answer.
            if len(answers["answer_start"]) == 0:
                tokenized["start_positions"].append(cls_index)
                tokenized["end_positions"].append(cls_index)
            else:
                # Start/end character index of the answer in the text.
                start_char = answers["answer_start"][0]
                end_char = start_char + len(answers["text"][0])
                
                # Start token index of the current span in the text.
                token_start_index = 0
                while sequence_ids[token_start_index] != 1:  # 1 is the context part
                    token_start_index += 1
                
                # End token index of the current span in the text.
                token_end_index = len(input_ids) - 1
                while sequence_ids[token_end_index] != 1:
                    token_end_index -= 1
                
                # Detect if the answer is out of the span (in which case this feature is labeled with the CLS index).
                if not (offsets[token_start_index][0] <= start_char and offsets[token_end_index][1] >= end_char):
                    tokenized["start_positions"].append(cls_index)
                    tokenized["end_positions"].append(cls_index)
                else:
                    # Otherwise move the token_start_index and token_end_index to the two ends of the answer.
                    # Note: we could go after the last offset if the answer is the last word (edge case).
                    while token_start_index < len(offsets) and offsets[token_start_index][0] <= start_char:
                        token_start_index += 1
                    tokenized["start_positions"].append(token_start_index - 1)
                    
                    while offsets[token_end_index][1] >= end_char:
                        token_end_index -= 1
                    tokenized["end_positions"].append(token_end_index + 1)
        
        return tokenized
        
    def train(self, output_dir: str = "akan_medical_model", num_train_epochs: int = 3):
        """
        Train the Akan medical model
        
        Args:
            output_dir: Directory to save the trained model
            num_train_epochs: Number of training epochs
        """
        print("Preparing training data...")
        dataset = self.prepare_akan_medical_data()
        
        # Convert to Hugging Face dataset
        train_dataset = Dataset.from_dict({
            "id": [str(i) for i in range(len(dataset))],
            "title": [""] * len(dataset),
            "context": [item["context"] for item in dataset],
            "question": [item["question"] for item in dataset],
            "answers": [{"text": item["answers"]["text"], 
                        "answer_start": item["answers"]["answer_start"]} 
                       for item in dataset]
        })
        
        # Tokenize the dataset
        print("Tokenizing dataset...")
        tokenized_datasets = train_dataset.map(
            self.tokenize_function,
            batched=True,
            remove_columns=train_dataset.column_names
        )
        
        # Define training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            evaluation_strategy="no",
            learning_rate=2e-5,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            num_train_epochs=num_train_epochs,
            weight_decay=0.01,
            push_to_hub=False,
            logging_dir='./logs',
            logging_steps=10,
            save_total_limit=3,
            save_strategy="epoch"
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_datasets,
            tokenizer=self.tokenizer,
        )
        
        # Start training
        print("Starting model training...")
        trainer.train()
        
        # Save the model
        print(f"Saving model to {output_dir}")
        trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        print("Training completed successfully!")
        return output_dir
    
    def prepare_akan_medical_data(self) -> list:
        """
        Prepare Akan medical training data from multiple sources
        Combines sample data with the medical knowledge base
        
        Returns:
            list: A list of training examples with context, question, and answers
        """
        # Sample Akan medical Q&A data
        sample_data = [
            # General health questions
            {
                "context": "Malaria yɛ ɔyare a ɛfi asan a ɛkɔ so wɔ ɔsram no nipadua mu.",
                "question": "Ɛdeɛn na ɛma ɔyare atiridii ba?",
                "answers": {
                    "text": ["Asan a ɛkɔ so wɔ ɔsram no nipadua mu"],
                    "answer_start": [0]
                }
            },
            # Symptom questions
            {
                "context": "Sɛ wowo atiridii a, ɛtumi de ɔhyew, awu, ne ahɔhohia aba wo.",
                "question": "Deɛn ne atiridii no nsɛn?",
                "answers": {
                    "text": ["ɔhyew, awu, ne ahɔhihia"],
                    "answer_start": [20]
                }
            },
            # Treatment questions
            {
                "context": "Wɔde nnuru te sɛ chloroquine, artemisinin-based combination therapies (ACTs) na ɛsa atiridii.",
                "question": "Deɛn na wɔde sa atiridii?",
                "answers": {
                    "text": ["chloroquine, artemisinin-based combination therapies (ACTs)"],
                    "answer_start": [5]
                }
            },
            # Prevention questions
            {
                "context": "Sɛ wubetumi a, fa net a wɔde twa atiridii ho hyia, fa nnuru a ɛkanyan atiridii, na fa nnebɔne a ɛkanyan atiridii a wɔde gu nsuo mu di dwuma.",
                "question": "Ɛte sɛn na mɛyɛ a mebɛyɛ mma atiridii annsa?",
                "answers": {
                    "text": ["fa net a wɔde twa atiridii ho hyia, fa nnuru a ɛkanyan atiridii, na fa nnebɔne a ɛkanyan atiridii a wɔde gu nsuo mu di dwuma"],
                    "answer_start": [14]
                }
            },
            {
                "context": "Ti yare yɛ ɔyare a ɛtaa ba wɔ stress, nsuo a wonnom, anaa ɔhaw foforɔ nti. Wɔtumi de home, nsuom, ne nnuro a ɛtumi te yea so sa.",
                "question": "Dɛn na ɛde ti yare ba?",
                "answer": "stress, nsuo a wonnom, anaa ɔhaw foforɔ",
                "answer_start": 45
            },
            {
                "context": "Ɔhyew yɛ nipadua no ɔkwan a ɔfa so ko tia nyarewa. Nipadua mu hyew a ɛyɛ dɛ yɛ 98.6°F (37°C). Ɔhyew a ɛboro 100.4°F (38°C) no na wɔfrɛ no ɔhyew.",
                "question": "Dɛn ne ɔhyew a ɛyɛ dɛ?",
                "answer": "98.6°F (37°C)",
                "answer_start": 85
            },
            {
                "context": "Ɔwa tumi yɛ amoa anaa nea ɛyɛ nsuo. Ɛtumi fi nyarewa, allergy, asthma, anaa ɔyare foforɔ mu ba. Ayaresa gyina nea ɛde ba no so.",
                "question": "Dɛn na ɛde ɔwa ba?",
                "answer": "nyarewa, allergy, asthma, anaa ɔyare foforɔ",
                "answer_start": 65
            }
        ]
        
        # Convert to dataset format
        dataset = Dataset.from_list(sample_data)
        
        return dataset
    
    def tokenize_data(self, dataset: Dataset) -> Dataset:
        """Tokenize the dataset for training"""
        
        def tokenize_function(examples):
            # Tokenize questions and contexts
            tokenized = self.tokenizer(
                examples["question"],
                examples["context"],
                truncation=True,
                padding=True,
                max_length=512,
                return_offsets_mapping=True
            )
            
            # Find answer positions in tokenized text
            start_positions = []
            end_positions = []
            
            for i, (answer_start, answer) in enumerate(zip(examples["answer_start"], examples["answer"])):
                # Find token positions for answers
                offset_mapping = tokenized["offset_mapping"][i]
                
                # Find start token
                start_token = 0
                for idx, (start, end) in enumerate(offset_mapping):
                    if start <= answer_start < end:
                        start_token = idx
                        break
                
                # Find end token
                end_token = start_token
                answer_end = answer_start + len(answer)
                for idx, (start, end) in enumerate(offset_mapping[start_token:], start_token):
                    if start < answer_end <= end:
                        end_token = idx
                        break
                
                start_positions.append(start_token)
                end_positions.append(end_token)
            
            tokenized["start_positions"] = start_positions
            tokenized["end_positions"] = end_positions
            
            # Remove offset mapping as it's not needed for training
            del tokenized["offset_mapping"]
            
            return tokenized
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        return tokenized_dataset
    
    def train_model(self, train_dataset: Dataset, output_dir: str = "./akan_medical_model"):
        """Fine-tune the model on Akan medical data"""
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            evaluation_strategy="no",  # No validation set in this example
            learning_rate=2e-5,
            per_device_train_batch_size=8,
            num_train_epochs=3,
            weight_decay=0.01,
            save_strategy="epoch",
            logging_dir=f"{output_dir}/logs",
            logging_steps=10,
            save_total_limit=2,
            load_best_model_at_end=False,
            dataloader_pin_memory=False,
        )
        
        # Data collator
        data_collator = DataCollatorWithPadding(
            tokenizer=self.tokenizer,
            padding=True
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
        )
        
        # Train the model
        print("Starting training...")
        trainer.train()
        
        # Save the model
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        print(f"Model saved to {output_dir}")
    
    def test_model(self, model_path: str):
        """Test the trained model"""
        
        # Load trained model
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForQuestionAnswering.from_pretrained(model_path)
        
        # Test questions
        test_cases = [
            {
                "context": "Ti yare yɛ ɔyare a ɛtaa ba wɔ stress, nsuo a wonnom, anaa ɔhaw foforɔ nti.",
                "question": "Dɛn na ɛde ti yare ba?"
            },
            {
                "context": "Ɔhyew yɛ nipadua no ɔkwan a ɔfa so ko tia nyarewa.",
                "question": "Dɛn ne ɔhyew?"
            }
        ]
        
        print("\nTesting trained model:")
        for i, test_case in enumerate(test_cases, 1):
            inputs = tokenizer(
                test_case["question"],
                test_case["context"],
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            
            with torch.no_grad():
                outputs = model(**inputs)
                start_scores = outputs.start_logits
                end_scores = outputs.end_logits
                
                # Get the most likely beginning and end of answer
                start_idx = torch.argmax(start_scores)
                end_idx = torch.argmax(end_scores)
                
                # Decode the answer
                answer_tokens = inputs["input_ids"][0][start_idx:end_idx+1]
                answer = tokenizer.decode(answer_tokens, skip_special_tokens=True)
                
                print(f"Test {i}:")
                print(f"Question: {test_case['question']}")
                print(f"Answer: {answer}")
                print(f"Confidence: {torch.max(start_scores).item():.3f}")
                print()

# Enhanced medical knowledge base with Akan translations
MEDICAL_KNOWLEDGE_BASE = {
    "symptoms": {
        "headache": {
            "en": {
                "description": "Pain or discomfort in the head or neck area",
                "causes": ["stress", "dehydration", "lack of sleep", "eye strain", "tension"],
                "treatments": ["rest", "hydration", "pain relievers", "cold/warm compress"],
                "when_to_see_doctor": "If severe, persistent, or accompanied by fever, vision changes, or neck stiffness"
            },
            "ak": {
                "description": "Ti mu yea anaa ɔhaw a ɛwɔ ti anaa kɔn mu",
                "causes": ["adwennwen", "nsuo a wonnom", "nna a wonnya", "aniwa mu haw", "honam mu nkitahodi"],
                "treatments": ["home", "nom nsuo pii", "nnuro a ɛtumi te yea so", "nsuonwini anaa hyew nneɛma"],
                "when_to_see_doctor": "Sɛ ɛyɛ den, ɛkɔ so, anaa ɔhyew, aniwa mu nsesa, anaa kɔn mu den ka ho a"
            }
        },
        "fever": {
            "en": {
                "description": "Elevated body temperature above normal (98.6°F/37°C)",
                "causes": ["infection", "inflammation", "heat exhaustion", "medication side effects"],
                "treatments": ["rest", "fluids", "fever reducers", "cool compress"],
                "when_to_see_doctor": "If temperature exceeds 103°F (39.4°C) or persists for more than 3 days"
            },
            "ak": {
                "description": "Nipadua mu hyew a ɛboro dɛ so (98.6°F/37°C)",
                "causes": ["nyarewa", "honam mu huru", "hyew mmoroso", "nnuro mu nsunsuanso"],
                "treatments": ["home", "nom nsuo pii", "nnuro a ɛtumi te ɔhyew so", "nsuonwini nneɛma"],
                "when_to_see_doctor": "Sɛ hyew no boro 103°F (39.4°C) anaa ɛkɔ so nna mmiɛnsa a"
            }
        },
        "cough": {
            "en": {
                "description": "Sudden expulsion of air from the lungs",
                "causes": ["cold", "flu", "allergies", "asthma", "smoking"],
                "treatments": ["honey", "warm liquids", "throat lozenges", "humidifier"],
                "when_to_see_doctor": "If cough persists over 2 weeks, produces blood, or is accompanied by high fever"
            },
            "ak": {
                "description": "Mframa a ɛfiri amoa mu prɛko pɛ",
                "causes": ["awɔ", "mframa yare", "allergy", "asthma", "tawa nom"],
                "treatments": ["ɛwo", "nsuonwini nneɛma", "menewa mu nnuro", "nsuo a ɛyɛ mframa"],
                "when_to_see_doctor": "Sɛ ɔwa no kɔ so nnawɔtwe mmienu, mogya fi mu ba, anaa ɔhyew kɛse ka ho a"
            }
        },
        "stomach_pain": {
            "en": {
                "description": "Discomfort or pain in the abdominal area",
                "causes": ["indigestion", "gas", "food poisoning", "ulcers", "appendicitis"],
                "treatments": ["rest", "bland foods", "hydration", "antacids"],
                "when_to_see_doctor": "If severe, persistent, or accompanied by vomiting, fever, or blood in stool"
            },
            "ak": {
                "description": "Yafunu mu yea anaa ɔhaw",
                "causes": ["aduane a woannyam yiye", "mframa", "aduane bɔne", "yafunu mu kuru", "appendix yare"],
                "treatments": ["home", "aduane a ɛnyɛ den", "nom nsuo", "nnuro a ɛtumi te yafunu mu yea so"],
                "when_to_see_doctor": "Sɛ ɛyɛ den, ɛkɔ so, anaa ɔfe ka ho, ɔhyew, anaa mogya wɔ ayamde mu a"
            }
        },
        "diarrhea": {
            "en": {
                "description": "Loose, watery bowel movements",
                "causes": ["food poisoning", "viral infection", "bacterial infection", "medication"],
                "treatments": ["hydration", "BRAT diet", "probiotics", "rest"],
                "when_to_see_doctor": "If severe dehydration, blood in stool, or persists more than 3 days"
            },
            "ak": {
                "description": "Ayamde a ɛyɛ nsuo na ɛyɛ ntɛntɛn",
                "causes": ["aduane bɔne", "mframa nyarewa", "bacteria nyarewa", "nnuro"],
                "treatments": ["nom nsuo pii", "aduane a ɛnyɛ den", "bacteria pa", "home"],
                "when_to_see_doctor": "Sɛ nsuo a wonnom no sa, mogya wɔ ayamde mu, anaa ɛkɔ so nna mmiɛnsa a"
            }
        }
    },
    "general_advice": {
        "en": {
            "emergency_signs": [
                "Difficulty breathing",
                "Chest pain",
                "Severe bleeding",
                "Loss of consciousness",
                "Severe allergic reaction"
            ],
            "prevention": [
                "Wash hands regularly",
                "Eat balanced diet",
                "Exercise regularly",
                "Get adequate sleep",
                "Stay hydrated"
            ]
        },
        "ak": {
            "emergency_signs": [
                "Home a ɛyɛ den",
                "Koko mu yea",
                "Mogya a ɛsen pii",
                "Nyanim a ɛyera",
                "Allergy a ɛyɛ den"
            ],
            "prevention": [
                "Hohoro wo nsa daa",
                "Di aduane a ɛyɛ",
                "Yɛ apɔmuden dwuma daa",
                "Da yiye",
                "Nom nsuo pii"
            ]
        }
    }
}

async def setup_medical_knowledge():
    """Setup medical knowledge base in MongoDB"""
    print("Setting up medical knowledge base...")
    
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client.akan_health_db
        
        # Clear existing knowledge base
        await db.medical_knowledge.delete_many({})
        
        # Insert new knowledge base
        knowledge_doc = {
            "_id": "medical_knowledge_v1",
            "version": "1.0",
            "created_at": datetime.utcnow(),
            "data": MEDICAL_KNOWLEDGE_BASE
        }
        
        await db.medical_knowledge.insert_one(knowledge_doc)
        
        # Create search indexes
        await db.medical_knowledge.create_index([("data.symptoms", "text")])
        
        print("✅ Medical knowledge base created")
        
        # Create sample health queries for testing
        sample_queries = [
            {
                "_id": "sample-query-1",
                "user_id": "test-user-id-456",
                "query_text": "I have a headache and feel tired",
                "query_language": "en",
                "response_text": "Headaches can be caused by stress, dehydration, lack of sleep, or eye strain. Try resting in a quiet, dark room, stay hydrated, and apply a cold compress. If the headache is severe or persistent, please consult a healthcare professional.",
                "response_language": "en",
                "confidence_score": "0.85",
                "model_used": "local_knowledge",
                "created_at": datetime.utcnow()
            },
            {
                "_id": "sample-query-2",
                "user_id": "akan-user-id-789",
                "query_text": "Me ti yea na me brɛ",
                "query_language": "ak",
                "response_text": "Ti yare betumi afi stress, nsuo a wonnom, nna a wonnya, anaa aniwa mu haw mu ba. Sɔ hwɛ sɛ wobɛhome wɔ komm ne sum beae, nom nsuo pii, na fa nsuonwini nneɛma to wo ti so. Sɛ ti yare no yɛ den anaa ɛkɔ so a, kɔ oduruyɛfoɔ nkyɛn.",
                "response_language": "ak",
                "confidence_score": "0.80",
                "model_used": "local_knowledge+akan",
                "created_at": datetime.utcnow()
            }
        ]
        
        for query in sample_queries:
            existing = await db.health_queries.find_one({"_id": query["_id"]})
            if not existing:
                await db.health_queries.insert_one(query)
                print(f"✅ Created sample query: {query['_id']}")
        
        print("✅ Medical knowledge base setup completed")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Medical knowledge setup failed: {e}")
        raise

async def main():
    """
    Main function to train the Akan medical model and set up the knowledge base
    """
    try:
        print("🚀 Starting Akan Medical Model Training")
        print("=" * 50)
        
        # Initialize MongoDB connection
        print("\n🔌 Initializing database connection...")
        from app.core.database import init_db
        await init_db()
        
        # Setup medical knowledge base
        print("📚 Setting up medical knowledge base...")
        await setup_medical_knowledge()
        
        # Initialize the model trainer
        print("\n🤖 Initializing Akan Medical Model Trainer...")
        trainer = AkanMedicalModelTrainer()
        
        # Load the base model
        print("🔍 Loading base multilingual model...")
        trainer.load_base_model()
        
        # Train the model
        print("\n🎓 Starting model training...")
        output_dir = trainer.train(
            output_dir="akan_medical_model",
            num_train_epochs=3  # Adjust based on your needs
        )
        
        print("\n✅ Training completed successfully!")
        print(f"📁 Model saved to: {output_dir}")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
