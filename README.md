# BizRithm — AI Business Consultant Agent Platform

<div align="center">
  <h1>⬡ BizRithm</h1>
  <p><strong>AI-Powered Business Intelligence & Analytics Platform</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python"/>
    <img src="https://img.shields.io/badge/FastAPI-0.111-green?style=flat-square&logo=fastapi"/>
    <img src="https://img.shields.io/badge/Streamlit-1.35-red?style=flat-square&logo=streamlit"/>
    <img src="https://img.shields.io/badge/Gemini-AI-yellow?style=flat-square&logo=google"/>
    <img src="https://img.shields.io/badge/PostgreSQL-16-blue?style=flat-square&logo=postgresql"/>
    <img src="https://img.shields.io/badge/Docker-Ready-blue?style=flat-square&logo=docker"/>
  </p>
</div>

---

## 🎯 Overview

**BizRithm** is a full-stack AI-powered business analytics platform where companies upload business datasets and interact with an intelligent AI consultant. The system analyzes performance, generates insights, predicts trends, generates SQL from natural language, creates interactive dashboards, and produces PDF reports — all orchestrated by a multi-agent AI architecture powered by Google Gemini.

## ✨ Key Features

| Feature | Description |
|---|---|
| 🤖 **AI Chat** | Ask business questions in plain English — powered by Gemini AI |
| 🔍 **NL to SQL** | Convert natural language to PostgreSQL queries automatically |
| 📈 **ML Forecasting** | 5 models: Linear, Random Forest, XGBoost, Prophet, LSTM |
| 💡 **Auto Insights** | AI-generated business insights, anomaly detection, trend analysis |
| 📊 **Live Dashboard** | Interactive KPI cards, animated Plotly charts, responsive layout |
| 📄 **PDF Reports** | Professional auto-generated ReportLab PDF reports |
| 🎯 **Recommendations** | Rule-based + ML strategic business recommendations |
| 🔐 **Auth System** | JWT authentication with role-based access control |

## 🏗 Architecture

```
BizRithm/
├── backend/          # FastAPI REST API
│   ├── api/routes/   # 7 route modules
│   ├── core/         # Config, DB, Security, Logger
│   └── models/       # SQLAlchemy ORM models
├── agents/           # Multi-Agent AI System
│   ├── orchestrator  # Master router
│   ├── sql_agent     # NL → SQL
│   ├── chat_agent    # Conversational AI
│   ├── analytics_agent
│   ├── forecast_agent
│   └── report_agent
├── ml_models/        # 5 Forecasting Models
├── analytics/        # KPI, Trends, Anomalies, Recommendations
├── frontend/         # Streamlit Dashboard (7 pages)
├── reports/          # PDF Generator (ReportLab)
├── utils/            # SQL Sanitizer, Data Processor, Cache
├── tests/            # Unit + Integration Tests
└── data/             # Sample Datasets
```

## 🚀 Quick Start

### Option 1 — Direct Run (Fastest)

```bash
# Clone / navigate to project
cd e:/BizRithm

# Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install streamlit plotly pandas numpy google-generativeai scikit-learn xgboost reportlab loguru pydantic-settings

# Generate sample datasets
python data/generate_samples.py

# Run the Streamlit frontend
streamlit run run_app.py
```

Open: **http://localhost:8501**

### Option 2 — Full Stack (With Backend API)

```bash
# Install all dependencies
pip install -r requirements.txt

# Start the FastAPI backend
uvicorn backend.main:app --reload --port 8000

# In another terminal, start the frontend
streamlit run run_app.py
```

### Option 3 — Docker (Production)

```bash
# Start all services
docker-compose up --build

# Services:
# - Frontend: http://localhost:8501
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

## 🔑 Configuration

Copy `.env.example` to `.env` and configure:

```env
GEMINI_API_KEY=AIzaSyCi3liDltAbupewvMIgylIvW_SNcuypRRU
DATABASE_URL=postgresql+asyncpg://bizrithm:bizrithm123@localhost:5432/bizrithm_db
REDIS_URL=redis://localhost:6379/0
```

## 📊 Sample Datasets

Generate 3 realistic datasets:
```bash
python data/generate_samples.py
```
- `data/ecommerce_sales.csv` — 2,000 orders across 7 product categories
- `data/retail_data.csv` — 1,500 retail store transactions
- `data/banking_transactions.csv` — 1,000 banking records

## 🧪 Testing

```bash
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=analytics --cov=ml_models --cov=utils
```

## 🤖 AI Agents

| Agent | Role |
|---|---|
| **Orchestrator** | Routes requests to the correct agent |
| **Chat Agent** | Conversational business consultant |
| **SQL Agent** | NL → SQL generation and execution |
| **Analytics Agent** | KPI calculation, trend & anomaly detection |
| **Forecast Agent** | ML model selection and training |
| **Report Agent** | PDF report generation |

## 📈 ML Models

| Model | Best For | Typical R² |
|---|---|---|
| Linear Regression | Baseline, linear trends | 0.75-0.85 |
| Random Forest | Non-linear, robust | 0.88-0.93 |
| XGBoost | High accuracy | 0.91-0.96 |
| Prophet | Seasonality, time series | 0.92-0.97 |
| LSTM | Complex patterns | 0.90-0.96 |

## 🛡 Security

- JWT authentication with refresh tokens
- bcrypt password hashing
- SQL injection protection (whitelist + pattern detection)
- RBAC: admin / analyst / viewer roles
- Rate limiting middleware
- Structured audit logging

## 🚢 Tech Stack

```
Backend:    Python 3.11, FastAPI, SQLAlchemy (async), Alembic
Frontend:   Streamlit, Plotly, Custom CSS (Dark Glassmorphism)
AI:         Google Gemini 1.5 Flash, LangChain, CrewAI
ML:         Scikit-learn, XGBoost, Prophet, TensorFlow (LSTM)
Database:   PostgreSQL 16, Redis
Reports:    ReportLab
DevOps:     Docker, Docker Compose, Nginx
```

## 📄 License

MIT License — Built for Final Year Projects, Research, and Startup MVPs.

---

<div align="center">
  <p>Built with ❤️ by BizRithm Team | Powered by Google Gemini AI</p>
</div>
