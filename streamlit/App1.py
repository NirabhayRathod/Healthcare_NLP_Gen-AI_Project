import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path
from sqlalchemy import create_engine

# Add the src folder to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.logger import logging
from src.drug_property_analyzer import get_drug_property_percentages
from src.summarization import call_summarization

# Load data
logging.info('dataset reading started for our Streamlit App')
try:
    engine = create_engine(
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{int(os.getenv('DB_PORT'))}/{os.getenv('DB_NAME')}",
        pool_pre_ping=True
    )
    logging.info("Connected to AWS RDS successfully")
except Exception as e:
    raise Exception(e, sys)

try:
    query = """
    SELECT *
    FROM processed_data
    """
    data = pd.read_sql(query, engine)
    logging.info("Dataset reading completed from AWS RDS to summarize the review")
except Exception as e:
    raise Exception(e, sys)

# Page configuration
st.set_page_config(
    page_title="Drug Review Analytics",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
        /* Main background and text colors */
        .main {
            background-color: #0e1117;
            color: #fafafa;
        }
        
        /* Titles */
        .main-title {
            font-size: 3rem !important;
            background: linear-gradient(45deg, #FF4B4B, #FF6B6B);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 800;
        }
        
        .section-title {
            font-size: 2rem !important;
            color: #FF6B6B;
            border-bottom: 2px solid #FF6B6B;
            padding-bottom: 0.5rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        
        /* Cards and containers */
        .feature-card {
            background: linear-gradient(135deg, #1e2229, #2d3746);
            padding: 1.5rem;
            border-radius: 15px;
            border-left: 4px solid #FF6B6B;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .metric-card {
            background: linear-gradient(135deg, #1e2229, #2d3746);
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #333;
            margin: 0.5rem;
        }
        
        /* Buttons */
        .stButton button {
            background: linear-gradient(45deg, #FF4B4B, #FF6B6B);
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 25px;
            font-size: 1.1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
        }
        
        /* Analysis sections */
        .analysis-section {
            background: linear-gradient(135deg, #1e2229, #2d3746);
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            border: 1px solid #333;
        }
        
        .success-box {
            background: #1a1f2b;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #00D4AA;
            margin: 1rem 0;
            color: #f0f0f0;
            line-height: 1.6;
        }
        
        /* Unified Property Analysis Styles */
        .property-container {
            background: linear-gradient(135deg, #1a1f2b, #2d3746);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid #333;
        }
        
        .property-header {
            color: #FF6B6B;
            font-size: 1.4rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            text-align: center;
            border-bottom: 2px solid #FF6B6B;
            padding-bottom: 0.5rem;
        }
        
        /* Rectangle Sections */
        .rectangle-section {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            border: 2px solid #333;
            transition: all 0.3s ease;
        }
        
        .rectangle-section:hover {
            border-color: #FF6B6B;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(255, 107, 107, 0.15);
        }
        
        .section-title-rectangle {
            color: #00D4AA;
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 1.2rem;
            display: flex;
            align-items: center;
            gap: 0.8rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #333;
        }
        
        /* Condition and Property Items inside Rectangles */
        .item-grid {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .condition-item, .property-item {
            background: rgba(255, 255, 255, 0.08);
            padding: 1.2rem;
            border-radius: 10px;
            border-left: 4px solid #FF6B6B;
            transition: all 0.3s ease;
        }
        
        .condition-item:hover, .property-item:hover {
            background: rgba(255, 255, 255, 0.12);
            transform: translateX(8px);
        }
        
        .item-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.8rem;
        }
        
        .condition-name, .property-name {
            color: #f0f0f0;
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .condition-stats, .property-stats {
            color: #FF6B6B;
            font-weight: 700;
            font-size: 1.1rem;
        }
        
        .progress-bar {
            background: rgba(255, 107, 107, 0.2);
            border-radius: 10px;
            height: 10px;
            margin-top: 0.8rem;
            overflow: hidden;
        }
        
        .progress-fill {
            background: linear-gradient(45deg, #FF4B4B, #FF6B6B);
            height: 100%;
            border-radius: 10px;
            transition: width 0.8s ease-in-out;
        }
        
        .property-description {
            color: #CCCCCC;
            font-size: 1rem;
            line-height: 1.5;
            margin-top: 0.5rem;
        }
        
        /* Summary Section Styles */
        .summary-container {
            background: linear-gradient(135deg, #1a1f2b, #2d3746);
            border-radius: 15px;
            padding: 2rem;
            margin: 1.5rem 0;
            border: 1px solid #333;
        }
        
        .summary-header {
            color: #FF6B6B;
            font-size: 1.6rem;
            font-weight: 800;
            text-align: center;
            margin-bottom: 2rem;
            border-bottom: 2px solid #FF6B6B;
            padding-bottom: 0.8rem;
        }
        
        .summary-drug-title {
            color: #00D4AA;
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        
        .summary-section {
            margin: 1.5rem 0;
            padding: 1.5rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            border-left: 4px solid;
        }
        
        .benefits-section {
            border-left-color: #00D4AA;
        }
        
        .side-effects-section {
            border-left-color: #FF6B6B;
        }
        
        .summary-section-title {
            color: #f0f0f0;
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .summary-list {
            color: #CCCCCC;
            font-size: 1.1rem;
            line-height: 1.8;
            margin-left: 1rem;
        }
        
        .summary-list li {
            margin: 0.5rem 0;
            padding-left: 0.5rem;
        }
        
        /* Creator Info Styles */
        .creator-info {
            text-align: center;
            margin-top: 3rem;
            padding: 1.5rem;
            background: linear-gradient(135deg, #1a1f2b, #2d3746);
            border-radius: 10px;
            border: 1px solid #333;
        }
        
        .creator-name {
            color: #FF6B6B;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .creator-email {
            color: #00D4AA;
            font-size: 1rem;
        }
        
        /* Table styling */
        .dataframe {
            background-color: #1e2229 !important;
            color: white !important;
        }
        
        .dataframe th {
            background-color: #FF6B6B !important;
            color: white !important;
        }
        
        .dataframe td {
            background-color: #2d3746 !important;
            color: white !important;
        }
        
        /* Icons */
        .icon {
            font-size: 1.3rem;
        }
    </style>
""", unsafe_allow_html=True)

def parse_property_data(property_results):
    """Parse the property results into conditions and medical properties"""
    conditions = []
    properties = []
    
    for result in property_results:
        if "Most Common Conditions for" in result:
            # This is a header, skip
            continue
        elif "reviews (" in result and "%" in result:
            # This is a condition line
            if ":" in result:
                condition_part = result.split(":")[0].strip()
                stats_part = result.split(":")[1].strip()
                conditions.append({
                    'name': condition_part,
                    'stats': stats_part
                })
        elif "mention" in result:
            # This is a medical property line
            properties.append(result)
    
    return conditions, properties

def create_property_analysis(input_drugname, property_results):
    """Create a cleaner, text-based property analysis section"""
    
    conditions, properties = parse_property_data(property_results)
    
    st.markdown(f"""
        <div class='property-container'>
            <div class='property-header'>
                🧪 Comprehensive Analysis for {input_drugname}
            </div>
    """, unsafe_allow_html=True)

    # 🎯 Most Common Conditions (Simple Text Style)
    if conditions:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #181c25, #222c38);
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                border-left: 4px solid #FF6B6B;
            ">
                <h3 style="color:#FF6B6B; margin-bottom:1rem;">🎯 Most Common Conditions</h3>
        """, unsafe_allow_html=True)

        for condition in conditions:
            st.markdown(f"""
                <div style="
                    background: rgba(255,255,255,0.05);
                    padding: 0.8rem 1rem;
                    margin: 0.5rem 0;
                    border-radius: 8px;
                    border-left: 3px solid #FF6B6B;
                ">
                    <strong style="color:#FAFAFA;">{condition['name']}</strong><br>
                    <span style="color:#BBBBBB; font-size:0.95rem;">{condition['stats']}</span>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ⚡ Medical Properties & Side Effects (Simple Text Style)
    if properties:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #181c25, #222c38);
                border-radius: 12px;
                padding: 1.5rem;
                margin-top: 1.5rem;
                border-left: 4px solid #00D4AA;
            ">
                <h3 style="color:#00D4AA; margin-bottom:1rem;">⚡ Medical Properties & Side Effects</h3>
        """, unsafe_allow_html=True)

        for prop in properties:
            st.markdown(f"""
                <div style="
                    background: rgba(255,255,255,0.05);
                    padding: 0.8rem 1rem;
                    margin: 0.5rem 0;
                    border-radius: 8px;
                    border-left: 3px solid #00D4AA;
                ">
                    <span style="color:#FAFAFA;">{prop}</span><br>
                    <span style="color:#BBBBBB; font-size:0.9rem;">Based on patient reviews and clinical feedback</span>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def create_summary_section(input_drugname, summary_text):
    """Create a beautifully formatted summary section"""
    
    st.markdown("""
        <div class='summary-container'>
            <div class='summary-header'>
                📝 AI-Powered Review Summary
            </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class='summary-drug-title'>
            Summary for <span style='color: #FF6B6B;'>{input_drugname}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Parse the summary text to extract benefits and side effects
    benefits = []
    side_effects = []
    current_section = None
    
    lines = summary_text.split('\n')
    for line in lines:
        line = line.strip()
        if 'benefits' in line.lower() or 'positive' in line.lower():
            current_section = 'benefits'
        elif 'side effects' in line.lower() or 'negative' in line.lower():
            current_section = 'side_effects'
        elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
            if current_section == 'benefits':
                benefits.append(line.lstrip('-•* ').strip())
            elif current_section == 'side_effects':
                side_effects.append(line.lstrip('-•* ').strip())
        elif line and current_section == 'benefits' and len(line) > 10:
            benefits.append(line)
        elif line and current_section == 'side_effects' and len(line) > 10:
            side_effects.append(line)
    
    # If no structured data found, use the entire summary
    if not benefits and not side_effects:
        st.markdown(f"""
            <div class='summary-section'>
                <div class='summary-section-title'>
                    📋 Overall Summary
                </div>
                <div style='color: #CCCCCC; font-size: 1.1rem; line-height: 1.6;'>
                    {summary_text}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Benefits Section
        if benefits:
            benefits_html = "".join([f"<li>{benefit}</li>" for benefit in benefits if benefit])
            st.markdown(f"""
                <div class='summary-section benefits-section'>
                    <div class='summary-section-title'>
                        ✅ Benefits
                    </div>
                    <ul class='summary-list'>
                        {benefits_html}
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        
        # Side Effects Section
        if side_effects:
            side_effects_html = "".join([f"<li>{effect}</li>" for effect in side_effects if effect])
            st.markdown(f"""
                <div class='summary-section side-effects-section'>
                    <div class='summary-section-title'>
                        ⚠️ Side Effects
                    </div>
                    <ul class='summary-list'>
                        {side_effects_html}
                    </ul>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def introduction_page():
    """Introduction page with overview and features"""
    
    st.markdown('<h1 class="main-title">💊 Drug Review Analytics Platform</h1>', unsafe_allow_html=True)
    
    # Hero Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
            <div style='text-align: center;'>
                <h2 style='color: #FF6B6B;'>Transform Drug Reviews into Actionable Insights</h2>
                <p style='font-size: 1.2rem; color: #CCCCCC;'>
                    Leverage advanced AI and NLP technologies to analyze drug effectiveness, 
                    side effects, and patient experiences from thousands of reviews.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/2069/2069571.png", width=150)
    
    st.markdown("---")
    
    # Key Features
    st.markdown('<h2 class="section-title">🚀 Key Features</h2>', unsafe_allow_html=True)
    
    features_col1, features_col2, features_col3 = st.columns(3)
    
    with features_col1:
        st.markdown("""
            <div class='feature-card'>
                <h3>🧪 Drug Property Analysis</h3>
                <p>Comprehensive analysis of drug effectiveness, side effects, and patient satisfaction metrics.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with features_col2:
        st.markdown("""
            <div class='feature-card'>
                <h3>📝 AI-Powered Summarization</h3>
                <p>Intelligent summarization of thousands of drug reviews using advanced NLP models.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with features_col3:
        st.markdown("""
            <div class='feature-card'>
                <h3>📊 Interactive Analytics</h3>
                <p>Interactive visualizations and metrics to understand drug performance across different conditions.</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Dataset Overview
    st.markdown('<h2 class="section-title">📊 Dataset Overview</h2>', unsafe_allow_html=True)
    
    # Metrics
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.markdown(f"""
            <div class='metric-card'>
                <h3>{len(data):,}</h3>
                <p>Total Reviews</p>
            </div>
        """, unsafe_allow_html=True)
    
    with metric_col2:
        st.markdown(f"""
            <div class='metric-card'>
                <h3>{len(data['drugName'].unique()):,}</h3>
                <p>Unique Drugs</p>
            </div>
        """, unsafe_allow_html=True)
    
    with metric_col3:
        st.markdown(f"""
            <div class='metric-card'>
                <h3>{len(data['conditions'].unique()):,}</h3>
                <p>Medical Conditions</p>
            </div>
        """, unsafe_allow_html=True)
    
    with metric_col4:
        avg_rating = data['rating'].mean()
        st.markdown(f"""
            <div class='metric-card'>
                <h3>{avg_rating:.1f}/10</h3>
                <p>Average Rating</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Sample Data Preview
    st.markdown('<h2 class="section-title">🔍 Data Preview</h2>', unsafe_allow_html=True)
    
    sample_data = data[['drugName', 'conditions', 'rating', 'review', 'usefulCount']].head(10)
    st.dataframe(sample_data, use_container_width=True)
    
    # Top Drugs by Review Count
    st.markdown('<h2 class="section-title">🏆 Top 10 Most Reviewed Drugs</h2>', unsafe_allow_html=True)
    
    top_drugs = data['drugName'].value_counts().head(10).reset_index()
    top_drugs.columns = ['Drug Name', 'Review Count']
    st.dataframe(top_drugs, use_container_width=True)
    
    # Analyze Button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div style='text-align: center; margin: 3rem 0;'>
                <h3 style='color: #FF6B6B; margin-bottom: 2rem;'>Ready to Analyze?</h3>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Start Drug Analysis", use_container_width=True):
            st.session_state.page = "analysis"
            st.rerun()
    
    # Creator Information
    st.markdown("---")
    st.markdown("""
        <div class='creator-info'>
            <div class='creator-name'>👨‍💻 Created by: Nirabhay Singh Rathod</div>
            <div class='creator-email'>📧 Email: nirbhay105633016@gmail.com</div>
        </div>
    """, unsafe_allow_html=True)

def analysis_page():
    """Main analysis page with drug selection and insights"""

    st.markdown('<h1 class="main-title">🔍 Drug Analysis Dashboard</h1>', unsafe_allow_html=True)

    # Back button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("⬅ Back to Introduction"):
            st.session_state.page = "introduction"
            st.rerun()

    st.markdown("---")

    # ==========================
    # Compact Sidebar
    # ==========================
    st.sidebar.markdown("""
        <div style='background: linear-gradient(135deg, #1e2229, #2d3746);
                    padding: 0.8rem; border-radius: 10px; margin-bottom: 1rem;'>
            <h3 style='color: #FF6B6B; margin: 0;'>🔍 Drug Selection</h3>
        </div>
    """, unsafe_allow_html=True)

    drug_names = sorted(data['drugName'].unique().tolist())

    input_drugname = st.sidebar.selectbox(
        "Choose your drug:",
        drug_names,
        key="drug_selector"
    )

    if input_drugname:
        drug_data = data[data['drugName'] == input_drugname]
        total_reviews = len(drug_data)
        avg_rating = drug_data['rating'].mean()
        top_condition = drug_data['conditions'].mode().iloc[0] if not drug_data.empty else "N/A"

        st.sidebar.markdown("---")
        st.sidebar.markdown(f"""
            <div style='font-size:0.9rem; color:#CCCCCC;'>
                <p><strong>Total Reviews:</strong> {total_reviews:,}</p>
                <p><strong>Avg Rating:</strong> {avg_rating:.1f}/10</p>
                <p><strong>Top Condition:</strong> {top_condition}</p>
            </div>
        """, unsafe_allow_html=True)

    # ==========================
    # MAIN CONTENT
    # ==========================
    if input_drugname:

        st.markdown(f"""
            <div style='text-align: center; background: linear-gradient(135deg, #1e2229, #2d3746); 
                        padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;'>
                <h2 style='color: #FF6B6B; margin: 0;'>Analysis for: {input_drugname}</h2>
            </div>
        """, unsafe_allow_html=True)

        # =====================================
        # 1️⃣ PROPERTY ANALYSIS (FIRST)
        # =====================================
        try:
            property_results = get_drug_property_percentages(input_drugname)
            create_property_analysis(input_drugname, property_results)
        except Exception as e:
            st.error(f"Error in drug property analysis: {str(e)}")

        # =====================================
        # 2️⃣ GRAPHS (SECOND)
        # =====================================
        drug_info = data[data['drugName'] == input_drugname]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
                <div class='analysis-section'>
                    <h3 style='color: #FF6B6B;'>📊 Rating Distribution</h3>
            """, unsafe_allow_html=True)

            rating_counts = drug_info['rating'].value_counts().sort_index()
            st.bar_chart(rating_counts)

            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("""
                <div class='analysis-section'>
                    <h3 style='color: #FF6B6B;'>🎯 Top Conditions</h3>
            """, unsafe_allow_html=True)

            condition_counts = drug_info['conditions'].value_counts().head(5)

            st.dataframe(
                condition_counts.reset_index().rename(
                    columns={'index': 'Condition', 'conditions': 'Count'}
                ),
                use_container_width=True,
                hide_index=True
            )

            st.markdown("</div>", unsafe_allow_html=True)

        # =====================================
        # 3️⃣ SUMMARY (LAST - WITH LOADING)
        # =====================================
        st.markdown("<br><br>", unsafe_allow_html=True)

        try:
            with st.spinner("Generating AI-powered summary... Please wait ⏳"):
                summary = call_summarization(input_drugname)

            create_summary_section(input_drugname, summary)

        except Exception as e:
            st.error(f"Error in summarization: {str(e)}")

        logging.info('Streamlit App worked Correctly')

    else:
        st.info("👈 Please select a drug from the sidebar to begin analysis.")


def main():
    """Main function to handle page navigation"""
    
    # Initialize session state for page navigation
    if 'page' not in st.session_state:
        st.session_state.page = "introduction"
    
    # Render the appropriate page
    if st.session_state.page == "introduction":
        introduction_page()
    elif st.session_state.page == "analysis":
        analysis_page()

if __name__ == "__main__":
    main()