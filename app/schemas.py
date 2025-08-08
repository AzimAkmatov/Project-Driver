from pydantic import BaseModel, EmailStr

class CompanyCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    address: str
from pydantic import BaseModel, EmailStr

class InviteUser(BaseModel):
    name: str
    email: EmailStr
    department: str
    
class DriverCreate(BaseModel):
    name: str
    dob: date
    license_number: str

class DriverResponse(BaseModel):
    id: int
    name: str
    dob: date
    license_number: str

    class Config:
        orm_mode = True
