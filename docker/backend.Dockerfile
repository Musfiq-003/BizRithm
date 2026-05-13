FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ curl libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY backend/ ./backend/
COPY agents/ ./agents/
COPY ml_models/ ./ml_models/
COPY analytics/ ./analytics/
COPY utils/ ./utils/
COPY reports/ ./reports/
COPY .env .

# Create required directories
RUN mkdir -p uploads logs reports/generated reports/charts ml_models/saved

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--loop", "uvloop"]
