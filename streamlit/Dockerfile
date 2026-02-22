FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgomp1 \
        gcc \
        curl \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements (from root context)
COPY streamlit/requirements.streamlit.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.streamlit.txt

# Download NLTK data
RUN python -m nltk.downloader punkt stopwords wordnet
COPY . /app/
EXPOSE 8501
CMD ["streamlit", "run", "streamlit/App1.py", "--server.port=8501", "--server.address=0.0.0.0"]