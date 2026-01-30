import pandas as pd
import numpy as np
import nltk
import re
import os
import sys
from sqlalchemy import create_engine
from dotenv import load_dotenv

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

load_dotenv()

engine = create_engine(
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{int(os.getenv('DB_PORT'))}/{os.getenv('DB_NAME')}",
    pool_pre_ping=True
)

nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")

query = """
SELECT
    uniqueID,
    drugName,
    conditions,
    review,
    rating,
    date,
    usefulCount
FROM raw_data
"""

data = pd.read_sql(query, engine)


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'&#?\w+;|http\S+|[^a-zA-Z\s]', '', text)
    text = ' '.join(text.split())
    return text

def tokenize_and_remove_stopwords(text):
    if not text:
        return ""
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    tokens = [t for t in tokens if t not in stop_words and len(t) > 2]

    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens]

    return " ".join(tokens)

data["review"] = data["review"].apply(clean_text)
data["review"] = data["review"].apply(tokenize_and_remove_stopwords)


benefit_keywords = [
    "effective", "works", "relief", "better", "improved",
    "help", "helps", "good", "great", "excellent",
    "amazing", "life changing", "wonderful"
]

side_effect_keywords = [
    "side effect", "nausea", "headache", "dizziness",
    "fatigue", "weight gain", "insomnia",
    "pain", "vomiting", "drowsiness"
]

data["benefit_mentions"] = data["review"].apply(
    lambda x: sum(1 for w in benefit_keywords if w in x)
)

data["side_effect_mentions"] = data["review"].apply(
    lambda x: sum(1 for w in side_effect_keywords if w in x)
)

data["review_date"] = pd.to_datetime(
    data["date"], format="%d-%b-%y", errors="coerce"
)

processed_df = data[
    [
        "uniqueID",
        "drugName",
        "conditions",
        "review",
        "rating",
        "review_date",
        "usefulCount",
        "benefit_mentions",
        "side_effect_mentions",
    ]
]


processed_df.to_sql(
    name="processed_data",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000
)

print("Processed data successfully stored in AWS RDS (processed_data)")
