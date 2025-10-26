"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- Application -> "application" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class Application(BaseModel):
    """
    Credit card application submissions
    Collection name: "application"
    """
    # Applicant inputs
    name: str = Field(..., description="Applicant full name")
    age: int = Field(..., ge=18, le=100, description="Age in years")
    income: float = Field(..., ge=0, description="Annual income in USD")
    employment_status: Literal['employed','self-employed','student','unemployed','retired'] = Field(...)
    employment_length: float = Field(..., ge=0, le=60, description="Years in current employment")
    credit_score: int = Field(..., ge=300, le=850, description="FICO score")
    debt_to_income: float = Field(..., ge=0, le=1, description="DTI ratio 0-1")
    existing_cards: int = Field(..., ge=0, le=20)
    late_payments: int = Field(..., ge=0, le=50)
    loan_amount: float = Field(..., ge=0, description="Requested credit limit")
    loan_purpose: str = Field(..., description="Purpose/notes")

    # Output fields
    approved: bool = Field(...)
    probability: float = Field(..., ge=0, le=1)
    explanation: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
