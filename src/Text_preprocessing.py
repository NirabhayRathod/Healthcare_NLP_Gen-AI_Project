import pandas as pd
import numpy as np
import nltk
import re
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from sqlalchemy import create_engine
from dotenv import load_dotenv
from logger import logging
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


def run_preprocessing():
    load_dotenv()
    
    engine = create_engine(
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{int(os.getenv('DB_PORT'))}/{os.getenv('DB_NAME')}",
        pool_pre_ping=True
    )
    logging.info("Connected to AWS RDS successfully")

    nltk.download("punkt")
    nltk.download("stopwords")
    nltk.download("wordnet")
    logging.info("punkt , stopwords , wordnet  downloaded")
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
    WHERE uniqueID NOT IN (
        SELECT uniqueID FROM processed_data
    );
    """

    data = pd.read_sql(query, engine)
    logging.info("sql data reading completed from raw_data table")

    def clean_text(text):
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'&#?\w+;|http\S+|[^a-zA-Z\s]', '', text)
        text = ' '.join(text.split())
        logging.info("'&#?\w+;|http\S+|[^a-zA-Z\s]' removed from review ")
        return text

    def tokenize_and_remove_stopwords(text):
        if not text:
            return ""
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words("english"))
        tokens = [t for t in tokens if t not in stop_words and len(t) > 2]

        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(t) for t in tokens]
        logging.info('tokenization and removing of stopwords done ')
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
    logging.info("two new column 'benifit_mensions & side_effect_mensions' created ")
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

    if processed_df.empty:
        print("No new data to process")
        return "No new records"

    processed_df.to_sql(
        name="processed_data",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000
    )
    logging.info('data stored in table processed_data')

    print(f"Processed {len(processed_df)} records")
    return f"Processed {len(processed_df)} records"


if __name__ == "__main__":
    run_preprocessing()
