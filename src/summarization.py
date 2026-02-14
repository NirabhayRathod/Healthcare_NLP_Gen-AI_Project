import pandas as pd
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
from sqlalchemy import create_engine
from logger import logging

load_dotenv()


try:
    engine = create_engine(
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{int(os.getenv('DB_PORT'))}/{os.getenv('DB_NAME')}",
        pool_pre_ping=True
    )
    logging.info("Connected to AWS RDS successfully")
except Exception as e:
    raise Exception(e, sys)


api_key = os.getenv("GROQ_API_KEY")

from langchain_groq import ChatGroq
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=api_key)

from langchain_core.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter


def get_combined_reviews(drug_name):
    logging.info(f"Fetching reviews for {drug_name} from AWS RDS")

    try:
        query = """
        SELECT review
        FROM processed_data
        WHERE drugName = %s
        LIMIT 200
        """

        drug_reviews = pd.read_sql(
            query,
            engine,
            params=(drug_name,)
        )

    except Exception as e:
        raise Exception(e, sys)

    if drug_reviews.empty:
        return ""

    max_reviews = 80
    if len(drug_reviews) > max_reviews:
        drug_reviews = drug_reviews.sample(n=max_reviews, random_state=42)

    combined_text = " ".join(drug_reviews["review"].astype(str))

    return combined_text


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


if __name__ == "__main__":
    print(call_summarization("Integra"))
