from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from typing import List, Optional

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
    department: str


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

    model_config = {
        "from_attributes": True
    }


# ---------- Driver Rating ----------

class DriverRatingCreate(BaseModel):
    driver_id: int
    score: int  # 1 to 5
    comment: Optional[str]


class DriverRatingResponse(BaseModel):
    id: int
    driver_id: int
    department: str
    score: int
    comment: Optional[str]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
