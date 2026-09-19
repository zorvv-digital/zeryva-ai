# 🛠️ Universal FastAPI & PostgreSQL Starter Boilerplate

A production-ready, highly modular starter template for building modern Python web APIs and microservices.

---

## 📁 Boilerplate Folder Structure

```text
zeryva-ai/
├── app/
│   ├── main.py              # FastAPI Application Entrypoint
│   ├── config/              # Application Settings & Environment Config
│   ├── db/                  # Async Database Session & Base Models
│   ├── models/              # Pydantic Request & Response DTO Schemas
│   ├── services/            # Service Layer & Business Logic Templates
│   └── api/                 # API Endpoint Routers
├── tests/                   # Pytest Unit & Integration Tests
├── requirements.txt         # Project Dependencies
└── .env.example             # Environment Variables Example
```

---

## ⚡ Quickstart Guide

### 1. Create & Activate Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 4. Run Development Server
```bash
uvicorn app.main:app --reload --port 8000
```

Access Interactive API Documentation at: `http://localhost:8000/docs`
