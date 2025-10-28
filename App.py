import streamlit as st
import pandas as pd
import sys
import os
# Add the src folder to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.exception import CustomException
from src.logger import logging


from src.drug_property_analyzer import get_drug_property_percentages
from src.summarization import call_summarization

# Load data
logging.info('dataset reading started for our Streamlit App')
try:
    data = pd.read_csv(r'D:\HEALTHCARE_NLP_GEN-AI_PROJECT\data\final_drug_review_data.csv')
    logging.info('data reading completed')
except Exception as e:
    raise CustomException(e ,sys)
# Streamlit app
def function():
    # Custom CSS for better UI
    st.markdown("""
        <style>
            /* Make main title larger */
            h1 {
                font-size: 2.4rem !important;
                color: #e0e6ed;
            }
            /* Dataset Overview header */
            h2 {
                color: #d0d7de;
            }
            /* Info sections (for analysis and summary) */
            .big-info {
                font-size: 1.3rem;
                font-weight: 700;
                color: #3fa9f5;
                margin-top: 25px;
                margin-bottom: 5px;
            }
            /* Success box smaller font - now white for dark theme */
            .small-success {
                font-size: 1rem;
                color: #ffffff; /* white text for visibility */
                line-height: 1.6;
            }
        </style>
    """, unsafe_allow_html=True)


    st.title("💊 Drug Review Analytics Platform")
    st.markdown("---")
    st.header("📊 Dataset Overview")

    # Top metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Drugs", len(data['drugName'].unique()))
    with col2:
        st.metric("Total Conditions", len(data['condition'].unique()))
    with col3:
        st.metric("Total Reviews", len(data))

    st.markdown("---")

    # Sidebar
    st.sidebar.header("🔍 Select Drug for Analysis")
    drug_names = data['drugName'].unique().tolist()
    input_drugname = st.sidebar.selectbox(
        "Choose your drug:",
        drug_names,
        placeholder="Type to search..."
    )

    if input_drugname:
        st.info(f"Selected: **{input_drugname}**")

        # 🔹 Drug property analysis section
        st.markdown(f"<div class='big-info'>🧪 Drug Property Analysis of <b>{input_drugname}</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='small-success'>{'<br>'.join(get_drug_property_percentages(input_drugname))}</div>", unsafe_allow_html=True)

        # 🔹 Summary section
        st.markdown(f"<div class='big-info'>📝 Summary of Reviews on <b>{input_drugname}</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='small-success'>{call_summarization(input_drugname)}</div>", unsafe_allow_html=True)
        logging.info('Streamlit App worked Correctly')
# Run the app
if __name__ == "__main__":
    function()
