import pandas as pd
import os, sys
from dotenv import load_dotenv
from sqlalchemy import create_engine

from logger import logging
from exception import CustomException

# -------------------------------
# ENV & DB SETUP
# -------------------------------
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

try:
    engine = create_engine(
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{int(os.getenv('DB_PORT'))}/{os.getenv('DB_NAME')}",
        pool_pre_ping=True
    )
    logging.info("Connected to AWS RDS successfully")
except Exception as e:
    raise CustomException(e, sys)

# -------------------------------
# LLM SETUP
# -------------------------------
from langchain_groq import ChatGroq
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=api_key)

from langchain_core.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter

# -------------------------------
# READ DATA FROM AWS RDS
# -------------------------------
logging.info("Dataset reading started for Summarization")

try:
    query = """
    SELECT drugName, review
    FROM processed_data
    """
    original_data = pd.read_sql(query, engine)
    logging.info("Dataset reading completed from AWS RDS")
except Exception as e:
    raise CustomException(e, sys)


def get_combined_reviews(drug_name):
    drug_reviews = original_data[
        original_data["drugName"] == drug_name
    ]["review"]

    if drug_reviews.empty:
        return ""

    # Always sample max 80 reviews
    max_reviews = 80
    if len(drug_reviews) > max_reviews:
        drug_reviews = drug_reviews.sample(n=max_reviews, random_state=42)

    combined_text = " ".join(drug_reviews.astype(str))
    return combined_text

# PROMPTS
map_template = """
Analyze this patient review portion for {drug_name}:
{text}
Extract benefits, side effects, and sentiment.
Keep it concise.
"""

map_prompt = PromptTemplate(
    input_variables=["text", "drug_name"],
    template=map_template
)

reduce_template = """
Combine these analyses for {drug_name}:
{text}
Provide final summary in this format:

**Summary for {drug_name}:**
- **Benefits:** [2-3 common benefits]
- **Side Effects:** [2-3 common side effects]
- **Overall Sentiment:** [brief assessment]
- **Key Insights:** [2-3 observations]
"""

reduce_prompt = PromptTemplate(
    input_variables=["text", "drug_name"],
    template=reduce_template
)

# SUMMARIZATION PIPELINE
def summarize_drug_reviews(drug_name, combined_reviews):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000,
        chunk_overlap=200
    )

    docs = text_splitter.create_documents([combined_reviews])

    summary_chain = load_summarize_chain(
        llm=llm,
        chain_type="map_reduce",
        map_prompt=map_prompt,
        combine_prompt=reduce_prompt,
        verbose=False
    )

    result = summary_chain.invoke({
        "input_documents": docs,
        "drug_name": drug_name
    })

    return result["output_text"]

def call_summarization(drug_name):
    text = get_combined_reviews(drug_name)
    if not text:
        return f"No reviews found for {drug_name}"
    return summarize_drug_reviews(drug_name, text)

# TEST
print(call_summarization("Integra"))
