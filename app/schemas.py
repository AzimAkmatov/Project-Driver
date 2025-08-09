from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------- Company ----------

class CompanyCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    address: str


# ---------- User Invite ----------

class InviteUser(BaseModel):
    name: str
    email: EmailStr
    department: str  # validated against allowed list in route


# ---------- Driver ----------

class DriverCreate(BaseModel):
    name: str
    dob: date
    license_number: str


class DriverResponse(BaseModel):
    id: int
    name: str
    dob: date
    license_number: str
    created_by_company_id: int

    # Pydantic v2: enable ORM conversion
    model_config = ConfigDict(from_attributes=True)


# ---------- Driver Rating ----------

class DriverRatingCreate(BaseModel):
    driver_id: int
    score: int = Field(..., ge=1, le=5)  # ensure 1..5
    comment: Optional[str] = None


class DriverRatingResponse(BaseModel):
    id: int
    driver_id: int
    user_id: int
    department: str
    score: int
    comment: Optional[str] = None
    # created_at: Optional[datetime] = None  # uncomment if you add it to the model

    model_config = ConfigDict(from_attributes=True)
