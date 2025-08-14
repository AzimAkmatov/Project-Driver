from datetime import date, datetime
from typing import Optional, Literal
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ---------- Enums / constants ----------

class Department(str, Enum):
    dispatch = "dispatch"
    hr = "hr"
    safety = "safety"
    accountant = "accountant"
    fleet_manager = "fleet_manager"

# ---------- Common responses ----------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class Message(BaseModel):
    message: str

# ---------- Company ----------

class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    address: str = Field(..., min_length=2, max_length=200)

class CompanyResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# ---------- User Invite / Staff ----------

class InviteUser(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    department: Department  # validated against enum

class StaffUserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: Department

    model_config = ConfigDict(from_attributes=True)

# ---------- Driver ----------

class DriverCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    dob: date
    license_number: str = Field(..., min_length=3, max_length=64)

class DriverResponse(BaseModel):
    id: int
    name: str
    dob: date
    license_number: str
    created_by_company_id: int

    model_config = ConfigDict(from_attributes=True)

# ---------- Driver Rating ----------

class DriverRatingCreate(BaseModel):
    driver_id: int
    score: int = Field(..., ge=1, le=5)  # ensure 1..5
    comment: Optional[str] = Field(None, max_length=2000)

class DriverRatingResponse(BaseModel):
    id: int
    driver_id: int
    user_id: int
    department: Department
    score: int
    comment: Optional[str] = None
    created_at: Optional[datetime] = None  # keep optional if not persisted yet

    model_config = ConfigDict(from_attributes=True)
