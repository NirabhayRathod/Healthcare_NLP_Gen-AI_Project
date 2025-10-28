import pandas as pd
import os , sys
from logger import logging
from exception import CustomException
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('GROQ_API_KEY')
from langchain_groq import ChatGroq
llm = ChatGroq(model='llama-3.1-8b-instant', api_key=api_key)

from langchain_core.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

logging.info('dataset reading started for Summarization')
try:
    original_data = pd.read_csv(r'D:\HEALTHCARE_NLP_GEN-AI_PROJECT\data\final_drug_review_data.csv')
    logging.info('dataset reading completed for summarizatin')
except Exception as e:
    raise CustomException(e, sys)
# combine whole review of that drugName with permanent sampling
def get_combined_reviews(drug_name):
    drug_reviews = original_data[original_data['drugName'] == drug_name]['review']
    
    if len(drug_reviews) == 0:
        return ""
    
    # PERMANENT: Always use max 80 reviews
    max_reviews = 80
    if len(drug_reviews) > max_reviews:
        drug_reviews = drug_reviews.sample(n=max_reviews, random_state=42)
            
    combined_text = " ".join(drug_reviews.astype(str))
    return combined_text

map_template = '''
Analyze this patient review portion for {drug_name}:
{text}
Extract benefits, side effects, and sentiment.
Keep it concise.
'''

map_prompt = PromptTemplate(
    input_variables=['text', 'drug_name'],
    template=map_template
)

reduce_template = '''
Combine these analyses for {drug_name}:
{text}
Provide final summary in this format:

**Summary for {drug_name}:**
- **Benefits:** [2-3 common benefits]
- **Side Effects:** [2-3 common side effects]  
- **Overall Sentiment:** [brief assessment]
- **Key Insights:** [2-3 observations]
'''

reduce_prompt = PromptTemplate(
    input_variables=['text', 'drug_name'],
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
        chain_type='map_reduce',
        map_prompt=map_prompt,
        combine_prompt=reduce_prompt,
        verbose=False
    )
    result = summary_chain.invoke({
        "input_documents": docs,
        "drug_name": drug_name
    })
    
    return result['output_text']

def call_summarization(drugName):
    text = get_combined_reviews(drugName)
    if not text:
        return f"No reviews found for {drugName}"
    return summarize_drug_reviews(drugName, text)

# Test
print(call_summarization('Integra'))