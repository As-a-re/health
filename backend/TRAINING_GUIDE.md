# Akan Medical Model Training Guide

This guide explains how to train and use the Akan language medical question-answering model.

## Prerequisites

- Python 3.8+
- pip
- Git
- MongoDB (local or remote connection)

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd virtual/backend
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Configure environment variables**
   Create a `.env` file in the backend directory with the following content:
   ```
   MONGODB_URL=mongodb://localhost:27017/akan_medical
   MODEL_PATH=./akan_medical_model
   ```

## Training the Model

1. **Prepare the training data**
   - Add your training examples to `prepare_akan_medical_data()` in `train_akan_model.py`
   - Ensure each example has a context, question, and answer with character positions

2. **Run the training script**
   ```bash
   python scripts/train_akan_model.py
   ```

3. **Monitor training progress**
   - Training logs will be saved to `./logs`
   - The model will be saved to `./akan_medical_model`

## Using the Trained Model

1. **Load the model in your application**
   ```python
   from transformers import AutoModelForQuestionAnswering, AutoTokenizer
   
   model_path = "./akan_medical_model"
   model = AutoModelForQuestionAnswering.from_pretrained(model_path)
   tokenizer = AutoTokenizer.from_pretrained(model_path)
   ```

2. **Make predictions**
   ```python
   def get_answer(question, context):
       inputs = tokenizer(question, context, return_tensors="pt")
       outputs = model(**inputs)
       answer_start = torch.argmax(outputs.start_logits)
       answer_end = torch.argmax(outputs.end_logits) + 1
       return tokenizer.convert_tokens_to_string(
           tokenizer.convert_ids_to_tokens(
               inputs["input_ids"][0][answer_start:answer_end]
           )
       )
   ```

## Model Architecture

The model is based on a multilingual BERT architecture fine-tuned on Akan medical Q&A pairs. It includes:

- Base model: `bert-base-multilingual-cased`
- Maximum sequence length: 384 tokens
- Batch size: 8
- Learning rate: 2e-5
- Training epochs: 3

## Adding More Training Data

To improve the model's performance, you can add more training examples by extending the `prepare_akan_medical_data()` method in `train_akan_model.py`. Each example should follow this format:

```python
{
    "context": "The context paragraph containing the answer",
    "question": "The question about the context",
    "answers": {
        "text": ["The exact answer text"],
        "answer_start": [character_position_of_answer_start]
    }
}
```

## Troubleshooting

- **CUDA Out of Memory**: Reduce the batch size in `TrainingArguments`
- **Training is slow**: Use a GPU if available, or reduce the model size
- **Poor performance**: Add more diverse training examples and increase training epochs

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
