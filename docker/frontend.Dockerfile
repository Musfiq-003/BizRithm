FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir streamlit streamlit-option-menu streamlit-extras plotly pandas numpy requests Pillow

COPY frontend/ ./frontend/
COPY .env .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"]
