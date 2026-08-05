# Seat CoC Page

Small FastAPI service that manages Certificate of Conformity (CoC) records for vehicle seats,
with a minimal HTML page for browsing them.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

Open http://localhost:8000/ for the HTML page, http://localhost:8000/docs for the API.

## Tests

```bash
pytest --cov=app --cov-report=term-missing
```
