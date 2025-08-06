# Corporate Email Categorization Model

This is a fine-tuned DistilBERT model for classifying corporate emails into various categories.

## Hugging Face Model

You can find and use the model on the Hugging Face Hub here:
[darshandugar/MailClassifier-DistilBERT](https://huggingface.co/darshandugar/MailClassifier-DistilBERT)

## Overview

This project focuses on building a robust model for corporate email categorization to automate the sorting and routing of internal and external communications. The process involves standard NLP techniques, data augmentation for handling class imbalance, and fine-tuning a pre-trained transformer model.

## Approach and Methodology

The fine-tuning process for this model followed these key steps:

1.  **Data Loading**: The initial dataset was loaded from the specified source.
2.  **Exploratory Data Analysis (EDA)**: Basic EDA was performed to understand the data structure, identify missing values, and analyze the distribution of labels.
3.  **Handling Data Imbalance**: It was observed that some categories had significantly fewer examples than others. To address this, data augmentation was employed.
4.  **Artificial Data Generation**: Synthetic email examples were generated for under-represented classes using the Groq API and the Llama3-8b-8192 model. This helped to balance the dataset and improve the model's ability to learn from minority classes.
5.  **Encoding**: String labels were converted into numerical representations (integer IDs) required for model training.
6.  **Tokenization**: The email text data was tokenized using the `distilbert-base-uncased` tokenizer. This process converts the text into a sequence of numerical tokens that the model can process, including adding special tokens and attention masks.
7.  **Data Splitting**: The combined original and augmented dataset was split into training, validation, and test sets to facilitate model training and evaluation.
8.  **Model Initialization**: A pre-trained `distilbert-base-uncased` model was loaded. For the classification task, output layers were added to the model to predict the defined categories.
9.  **Training**: The model was fine-tuned on the augmented training dataset using the Hugging Face `Trainer`. The training involved optimizing the model's parameters to minimize the classification loss.
10. **Evaluation**: The fine-tuned model's performance was evaluated on a separate, unseen test set.

## Training Details

*   **Base Model**: `distilbert-base-uncased`
*   **Training Method**: Fine-tuning with added output layers for sequence classification. (While LoRA was mentioned, the provided notebook code does not explicitly show LoRA implementation. This description reflects the standard fine-tuning with classification layers as seen in the code.)
*   **Epochs**: 5
*   **Batch Size**: 16 (Training and Evaluation)
*   **Optimizer**: AdamW
*   **Learning Rate Scheduler**: Linear warmup
*   **Loss Function**: Cross-Entropy Loss (implicitly used by `AutoModelForSequenceClassification`)

## Evaluation Results

The model's performance on the final test set is summarized below:

| Metric             | Value    |
|--------------------|----------|
|accuracy           |  0.9130 |
| f1_weighted        |  0.7949 |
| precision_weighted |  0.8462 |
| recall_weighted    |  0.7692
