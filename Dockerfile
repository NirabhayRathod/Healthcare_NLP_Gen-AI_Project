FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y \
        build-essential \
        libgomp1 \
        curl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m nltk.downloader punkt stopwords wordnet

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "App1.py", "--server.port=8501", "--server.address=0.0.0.0"]
