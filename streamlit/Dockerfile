FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgomp1 \
        curl \
        gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.streamlit.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.streamlit.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Copy the entire project
COPY . .

# Create necessary directories if they don't exist
RUN mkdir -p /app/src /app/streamlit

# Move summarization.py to the correct location if needed
# (Uncomment if you want to move it)
# RUN cp summarization.py /app/src/ 2>/dev/null || :

# Expose port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "streamlit/App1.py", "--server.port=8501", "--server.address=0.0.0.0"]