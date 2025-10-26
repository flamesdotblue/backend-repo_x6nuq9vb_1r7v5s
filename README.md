# Credit Card Approval API

Secure REST API for credit card approval decisions with probability, explanations, and next steps.

- Auth: API key via header `x-api-key`
- Endpoint: `POST /predict`
- Tech: FastAPI + MongoDB (optional logging)

## Quick start

1) Configure environment (optional but recommended):

- Set `API_KEY` to your secret key
- Set `DATABASE_URL` and `DATABASE_NAME` to enable MongoDB logging

Example `.env`:

```
API_KEY=dev-key-123
DATABASE_URL=mongodb+srv://<user>:<pass>@<cluster>/
DATABASE_NAME=app
```

2) Install and run (in this repo):

```
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Sample request

POST /predict

Headers:
- `Content-Type: application/json`
- `x-api-key: dev-key-123`

Body:
```
{
  "name": "Jane Doe",
  "age": 32,
  "income": 85000,
  "employment_status": "employed",
  "employment_length": 4,
  "credit_score": 720,
  "debt_to_income": 0.28,
  "existing_cards": 2,
  "late_payments": 0,
  "loan_amount": 5000,
  "loan_purpose": "Everyday purchases"
}
```

Sample response:
```
{
  "approved": true,
  "probability": 0.78,
  "explanation": [
    "Good credit history",
    "Healthy debt-to-income ratio",
    "Requested limit aligned with income",
    "No recent late payments",
    "Stable employment"
  ],
  "next_steps": [
    "Verify identity (KYC)",
    "Link income documents (pay stubs or bank statements)",
    "E-sign cardholder agreement"
  ]
}
```

Notes:
- `probability` is a heuristic score (0–1) based on credit score, DTI, income vs requested limit, pay history, and employment stability.
- All prediction requests are logged to the `application` collection when database is configured.

## Running tests

```
pytest -q
```

## Deployment

- Set `API_KEY` to a strong secret in your environment
- Provide `DATABASE_URL` and `DATABASE_NAME` for production logging
- Run with a production server such as uvicorn or gunicorn:

```
uvicorn main:app --host 0.0.0.0 --port 8000
```

Behind a reverse proxy, ensure TLS termination and allow the frontend origin via CORS if restricting origins.
