import pandas as pd
import numpy as np
import nltk
import re
import string
import os
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Create directories if they don't exist
os.makedirs('data', exist_ok=True)
os.makedirs('models', exist_ok=True)

# Load data
data = pd.read_csv(r'D:\Healthcare-NLP-and-Generative-AI-Projects\data\cleaned_drugCom_raw.csv')

def clean_text(text):
    if isinstance(text, float):
        return ""
    text = text.lower()
    text = re.sub(r'&#?\w+;|http\S+|[^a-zA-Z\s]', '', text)
    text = ' '.join(text.split())
    return text

def tokenize_and_remove_stopwords(text):
    if not text:
        return []
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]
    
    return ' '.join(lemmatized_tokens)

# Apply text preprocessing
data['review'] = data['review'].apply(clean_text)
data['review'] = data['review'].apply(tokenize_and_remove_stopwords) 

benefit_keywords = ['effective', 'works', 'relief', 'better', 'improved', 'help', 'helps',
                   'good', 'great', 'excellent', 'amazing', 'life changing', 'wonderful']

side_effect_keywords = ['side effect', 'nausea', 'headache', 'dizziness', 'fatigue',
                       'weight gain', 'insomnia', 'pain', 'vomiting', 'drowsiness']

data['benefit_mentions'] = data['review'].apply(
    lambda x: sum(1 for word in benefit_keywords if word in x)
)

data['side_effect_mentions'] = data['review'].apply(
    lambda x: sum(1 for word in side_effect_keywords if word in x)
)

essential_columns = [
    'drugName', 'condition', 'review', 'rating', 'date', 
    'usefulCount', 'benefit_mentions', 'side_effect_mentions'
]
data = data[essential_columns]

data.to_csv(r'D:\Healthcare-NLP-and-Generative-AI-Projects\data\final_drug_review_data.csv', index=False)