from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, database
from ..auth import get_current_staff_user

router = APIRouter(prefix="/staff", tags=["Staff"])

@router.get("/drivers")
def get_all_drivers(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_staff_user),
):
    # Example protected endpoint: list all drivers for this company only
    return db.query(models.Driver).filter(models.Driver.created_by_company_id == current_user.company_id).all()
