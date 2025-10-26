import os
from typing import List, Literal
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import create_document

app = FastAPI(title="Credit Card Approval API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Applicant(BaseModel):
    name: str
    age: int = Field(..., ge=18, le=100)
    income: float = Field(..., ge=0)
    employment_status: Literal['employed','self-employed','student','unemployed','retired']
    employment_length: float = Field(..., ge=0, le=60)
    credit_score: int = Field(..., ge=300, le=850)
    debt_to_income: float = Field(..., ge=0, le=1)
    existing_cards: int = Field(..., ge=0, le=20)
    late_payments: int = Field(..., ge=0, le=50)
    loan_amount: float = Field(..., ge=0)
    loan_purpose: str


class PredictResponse(BaseModel):
    approved: bool
    probability: float = Field(..., ge=0, le=1)
    explanation: List[str]
    next_steps: List[str]


def require_api_key(x_api_key: str | None) -> None:
    expected = os.getenv("API_KEY", "dev-key-123")
    if not x_api_key or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/")
def read_root():
    return {"message": "Credit Card Approval API", "docs": "/docs"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


@app.post("/predict", response_model=PredictResponse)
def predict(applicant: Applicant, x_api_key: str | None = Header(default=None, alias="x-api-key")):
    # API key auth
    require_api_key(x_api_key)

    # Simple rule-based scoring model (0 to 1)
    score = 0.0
    reasons: List[str] = []

    # Credit score contribution
    score += max(0, (applicant.credit_score - 300)) / 550 * 0.4  # up to 0.4
    if applicant.credit_score >= 740:
        reasons.append("Excellent credit history")
    elif applicant.credit_score >= 680:
        reasons.append("Good credit history")
    elif applicant.credit_score < 600:
        reasons.append("Low credit score lowers approval odds")

    # Debt-to-income ratio (lower is better)
    dti = applicant.debt_to_income
    score += max(0, (0.6 - dti)) / 0.6 * 0.25  # up to 0.25
    if dti <= 0.25:
        reasons.append("Healthy debt-to-income ratio")
    elif dti > 0.45:
        reasons.append("High debt burden reduces eligibility")

    # Income vs requested limit
    affordability = min(1.0, applicant.income / max(1.0, applicant.loan_amount * 2))
    score += affordability * 0.15
    if affordability >= 0.7:
        reasons.append("Requested limit aligned with income")
    else:
        reasons.append("Requested limit high relative to income")

    # Payment history and cards
    late_factor = max(0, 1 - applicant.late_payments / 12)
    score += late_factor * 0.1
    if applicant.late_payments == 0:
        reasons.append("No recent late payments")
    elif applicant.late_payments > 3:
        reasons.append("Multiple late payments on record")

    # Employment stability
    if applicant.employment_status in ["employed", "self-employed"]:
        score += min(1, applicant.employment_length / 10) * 0.1
        if applicant.employment_length >= 2:
            reasons.append("Stable employment")
        else:
            reasons.append("Limited employment history")
    elif applicant.employment_status == "student":
        reasons.append("Student status considered higher risk")
    else:
        reasons.append("Current employment status reduces eligibility")

    probability = max(0.0, min(1.0, score))
    approved = probability >= 0.6

    next_steps = (
        [
            "Verify identity (KYC)",
            "Link income documents (pay stubs or bank statements)",
            "E-sign cardholder agreement",
        ]
        if approved
        else [
            "Consider lowering requested limit",
            "Reduce debt-to-income ratio",
            "Improve credit score and reapply in 60–90 days",
            "Optionally provide a co-signer or additional income proof",
        ]
    )

    # Persist application summary in DB (best-effort)
    try:
        create_document(
            "application",
            {
                **applicant.model_dump(),
                "approved": approved,
                "probability": probability,
                "explanation": reasons,
                "next_steps": next_steps,
            },
        )
    except Exception:
        # Database is optional for prediction flow
        pass

    return PredictResponse(
        approved=approved,
        probability=probability,
        explanation=reasons,
        next_steps=next_steps,
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
