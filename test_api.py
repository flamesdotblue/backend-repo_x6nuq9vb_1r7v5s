from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

API_KEY = os.getenv("API_KEY", "dev-key-123")


def test_predict_auth_required():
    payload = {
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
        "loan_purpose": "Everyday purchases",
    }

    # Missing key
    r = client.post("/predict", json=payload)
    assert r.status_code == 401

    # Wrong key
    r = client.post("/predict", headers={"x-api-key": "wrong"}, json=payload)
    assert r.status_code == 401


def test_predict_success_shape():
    payload = {
        "name": "John Smith",
        "age": 40,
        "income": 120000,
        "employment_status": "employed",
        "employment_length": 8,
        "credit_score": 760,
        "debt_to_income": 0.2,
        "existing_cards": 3,
        "late_payments": 0,
        "loan_amount": 7000,
        "loan_purpose": "Travel",
    }
    r = client.post("/predict", headers={"x-api-key": API_KEY}, json=payload)
    assert r.status_code == 200
    data = r.json()
    assert set(data.keys()) == {"approved", "probability", "explanation", "next_steps"}
    assert isinstance(data["approved"], bool)
    assert 0 <= data["probability"] <= 1
    assert isinstance(data["explanation"], list)
    assert isinstance(data["next_steps"], list)
