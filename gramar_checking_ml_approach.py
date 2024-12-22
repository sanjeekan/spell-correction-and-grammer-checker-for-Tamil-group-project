# -*- coding: utf-8 -*-
"""gramar checking ml approach.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1k1HETDxpA1TJ96_Hldsqg_HsjZEeOEss
"""

pip install transformers datasets torch sentencepiece

from huggingface_hub import login

login(token="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")

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq
from datasets import Dataset, DatasetDict
import pandas as pd

# Load Custom Dataset with Train-Test Split
def load_custom_dataset(file_path):
    data = pd.read_excel(file_path)
    dataset = Dataset.from_pandas(data)
    train_test_split = dataset.train_test_split(test_size=0.2, seed=42)
    return DatasetDict({"train": train_test_split["train"], "test": train_test_split["test"]})

# 2. Initialize Model and Tokenizer
model_name = "google/mt5-small"  # Supports Tamil language
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# 3. Tokenize Data
def preprocess_data(examples):
    inputs = examples["paragraphs"]
    targets = examples["corrected_paragraphs"]
    model_inputs = tokenizer(inputs, max_length=128, truncation=True, padding="max_length")
    labels = tokenizer(text_target=targets, max_length=128, truncation=True, padding="max_length")
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# 4. Load Dataset and Preprocess
file_path = "/content/drive/MyDrive/dataset.xlsx"
dataset = load_custom_dataset(file_path)
tokenized_datasets = dataset.map(preprocess_data, batched=True)

# 5. Data Collator for Dynamic Padding
data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

# 6. Define Training Arguments
training_args = Seq2SeqTrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    weight_decay=0.01,
    save_total_limit=3,
    num_train_epochs=3,
    predict_with_generate=True,
    logging_dir="./logs",
    logging_steps=10,
    save_steps=500,
)

# 7. Initialize Trainer
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["test"],
    tokenizer=tokenizer,
    data_collator=data_collator,
)

# 8. Fine-tune the Model
trainer.train()

# Save the fine-tuned model
model.save_pretrained("./fine_tuned_tamil_model")
tokenizer.save_pretrained("./fine_tuned_tamil_model")

# 9. Grammar Correction Function (No changes needed here)
def correct_grammar(paragraph):
    inputs = tokenizer(paragraph, return_tensors="pt", truncation=True, max_length=128, padding="max_length")
    outputs = model.generate(
        inputs.input_ids,
        max_length=128,
        num_beams=5,
        early_stopping=True,
        length_penalty=1.0  # Penalize very short outputs
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# 10. Correct Paragraphs from an Excel File
input_file = "/content/drive/MyDrive/input.xlsx"  # Input file path
output_file = "/content/drive/MyDrive/corrected_output.xlsx"  # Output file path

# Read the input Excel file
df = pd.read_excel(input_file)

# Specify the column containing the paragraphs to correct
input_column = "paragraphs"  # Replace with the actual column name
output_column = "corrected_paragraphs"

# Correct each paragraph and store the results
df[output_column] = df[input_column].apply(lambda x: correct_grammar(x) if isinstance(x, str) else "")

# Save the corrected paragraphs to a new Excel file
df.to_excel(output_file, index=False)

print(f"Corrected paragraphs saved to {output_file}")