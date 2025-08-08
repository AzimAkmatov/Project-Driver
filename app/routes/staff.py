from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, database
from app.auth import get_current_staff_user

router = APIRouter(prefix="/staff", tags=["Staff"])

# Example endpoint: Get all drivers (staff only)
@router.get("/drivers")
def get_all_drivers(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_staff_user)):
    return db.query(models.Driver).all()
