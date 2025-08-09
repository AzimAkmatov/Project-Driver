from typing import List, Optional
from datetime import datetime, timedelta, timezone, date

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext

# Local (package-relative) imports — avoid rebinding "app"
from . import models, schemas, utils
from .database import get_db, Base, engine
from .routes import ping, staff
from .auth import get_current_staff_user as get_current_staff
from .core.settings import settings

SECRET_KEY = settings.SECRET_KEY
STAFF_SECRET_KEY = settings.STAFF_SECRET_KEY
DATABASE_URL = settings.DATABASE_URL
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = HTTPBearer()

# FastAPI app
app = FastAPI()
app.include_router(ping.router)
app.include_router(staff.router)

# ------------------ UTILS ------------------

def create_access_token(data: dict, secret_key: str, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)

# ------------------ AUTH HELPERS ------------------

def get_current_company(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        company_id_raw = payload.get("sub")
        company_id: int | None = int(company_id_raw) if company_id_raw is not None else None
        if company_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if company is None:
        raise credentials_exception
    return company

# ------------------ CEO ROUTES ------------------

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
        address=company.address,
    )
    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return {"message": "Company registered successfully", "company_id": new_company.id}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.email == form_data.username).first()
    if not company or not utils.verify_password(form_data.password, company.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(company.id)}, secret_key=SECRET_KEY)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/company/me")
def read_company_me(current_company: models.Company = Depends(get_current_company)):
    return {
        "id": current_company.id,
        "name": current_company.name,
        "email": current_company.email,
        "address": current_company.address,
    }

@app.post("/invite-user")
def invite_user(
    user: schemas.InviteUser,
    db: Session = Depends(get_db),
    current_company: models.Company = Depends(get_current_company),
):
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
        company_id=current_company.id,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": f"{user.department} invited successfully",
        "user_id": new_user.id,
        "default_password": "changeme123",
    }

@app.get("/company/staff")
def get_company_staff(
    current_company: models.Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    staff_users = db.query(models.User).filter(models.User.company_id == current_company.id).all()
    return [
        {"id": u.id, "name": u.name, "email": u.email, "department": u.department}
        for u in staff_users
    ]

# ------------------ STAFF ROUTES ------------------

@app.post("/staff-login")
def staff_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    staff_user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not staff_user or not utils.verify_password(form_data.password, staff_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(staff_user.id)}, secret_key=STAFF_SECRET_KEY)
    return {"access_token": access_token, "token_type": "bearer"}

# ------------------ DRIVER MANAGEMENT ------------------

@app.post("/drivers", response_model=schemas.DriverResponse)
def create_driver(
    driver: schemas.DriverCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_company),
):
    existing = db.query(models.Driver).filter(models.Driver.license_number == driver.license_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Driver already exists")

    new_driver = models.Driver(
        name=driver.name,
        dob=driver.dob,
        license_number=driver.license_number,
        created_by_company_id=current_user.id,
    )
    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    return new_driver

@app.get("/drivers/search", response_model=List[schemas.DriverResponse])
def search_drivers(
    name: str = "",
    dob: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_company),
):
    query = db.query(models.Driver).filter(models.Driver.created_by_company_id == current_user.id)

    if name:
        query = query.filter(models.Driver.name.ilike(f"%{name}%"))
    if dob:
        query = query.filter(models.Driver.dob == dob)

    return query.all()

@app.get("/drivers/{driver_id}", response_model=schemas.DriverResponse)
def get_driver(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_company),
):
    driver = db.query(models.Driver).filter_by(id=driver_id, created_by_company_id=current_user.id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver

# ------------------ DRIVER RATING ------------------

@app.post("/ratings", response_model=schemas.DriverRatingResponse)
def rate_driver(
    rating: schemas.DriverRatingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_staff),
):
    driver = db.query(models.Driver).filter(models.Driver.id == rating.driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    if driver.created_by_company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="You can only rate drivers from your company")

    new_rating = models.DriverRating(
        driver_id=rating.driver_id,
        user_id=current_user.id,
        department=current_user.department,
        score=rating.score,
        comment=rating.comment,
    )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating

@app.get("/drivers/{driver_id}/ratings", response_model=List[schemas.DriverRatingResponse])
def get_driver_ratings(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_company),
):
    driver = db.query(models.Driver).filter_by(id=driver_id, created_by_company_id=current_user.id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver.ratings

#Silence favicon
from fastapi import Response

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

