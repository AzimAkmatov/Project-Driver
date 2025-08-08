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
