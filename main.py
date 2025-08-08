from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app import models, schemas, database, utils
from app.routes import ping, staff
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

app = FastAPI()
app.include_router(ping.router)
app.include_router(staff.router)

# Dependencies
get_db = database.get_db
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CEO JWT Config
SECRET_KEY = "your-secret-key"  # ❗ Replace for production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Staff JWT Config
STAFF_SECRET_KEY = "staff-secret-key"  # ❗ Replace for production

# OAuth2
oauth2_scheme = HTTPBearer()

# Helpers
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

from datetime import datetime, timedelta, timezone

def create_access_token(data: dict, secret_key: str, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)


# CEO Registration
@app.post("/register")
def register_company(company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Company).filter(models.Company.email == company.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = utils.hash_password(company.password)
    new_company = models.Company(
        name=company.name,
        email=company.email,
        password=hashed_pw,
        address=company.address
    )
    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return {"message": "Company registered successfully", "company_id": new_company.id}

# CEO Login
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.email == form_data.username).first()
    if not company or not verify_password(form_data.password, company.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(company.id)}, secret_key=SECRET_KEY)
    return {"access_token": access_token, "token_type": "bearer"}

# Get current company (CEO)
def get_current_company(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        company_id: int = int(payload.get("sub"))
        if company_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if company is None:
        raise credentials_exception
    return company

# Get CEO profile
@app.get("/company/me")
def read_company_me(current_company: models.Company = Depends(get_current_company)):
    return {
        "id": current_company.id,
        "name": current_company.name,
        "email": current_company.email,
        "address": current_company.address
    }

# Invite Staff
@app.post("/invite-user")
def invite_user(user: schemas.InviteUser, db: Session = Depends(get_db), current_company: models.Company = Depends(get_current_company)):
    allowed_departments = {"dispatch", "hr", "safety", "accountant", "fleet_manager"}

    if user.department not in allowed_departments:
        raise HTTPException(status_code=400, detail="Invalid department")

    existing = db.query(models.User).filter_by(company_id=current_company.id, department=user.department).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"{user.department} already exists in your company")

    hashed_pw = utils.hash_password("changeme123")  # Default password
    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_pw,
        department=user.department,
        company_id=current_company.id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": f"{user.department} invited successfully", "user_id": new_user.id, "default_password": "changeme123"}

# List Staff Users
@app.get("/company/staff")
def get_company_staff(current_company: models.Company = Depends(get_current_company), db: Session = Depends(get_db)):
    staff = db.query(models.User).filter(models.User.company_id == current_company.id).all()
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "department": user.department
        }
        for user in staff
    ]

# Staff Login
@app.post("/staff-login")
def staff_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    staff_user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not staff_user or not utils.verify_password(form_data.password, staff_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(staff_user.id)}, secret_key=STAFF_SECRET_KEY)
    return {"access_token": access_token, "token_type": "bearer"}
