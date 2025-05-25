# StatusPage Backend

This is the backend service for the StatusPage application using Python (FastAPI).

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Docker & Docker Compose (optional but recommended)

### Installation

1. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
python run_migrations.py
```

4. Start the backend:

```bash
uvicorn main:app --reload
```

App will be available at [http://localhost:8000](http://localhost:8000)

---

## 🐳 Docker (Optional)

```bash
docker-compose up --build
```

---

## 📁 Project Structure

- `api/` – route definitions
- `models/` – ORM models
- `schemas/` – Pydantic schemas
- `core/` – application configuration
- `db/` – database utilities
- `migrations/` – Alembic migrations

---

## 🔐 Environment Variables

Copy the example file and update accordingly:

```bash
cp .env.example .env
```