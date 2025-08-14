# backend/app/db/models.py
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, Date, DateTime, ForeignKey, Enum as SAEnum, UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import Base


class DepartmentEnum(str, Enum):
    dispatch = "dispatch"
    hr = "hr"
    safety = "safety"
    accountant = "accountant"
    fleet_manager = "fleet_manager"


# -------- Company --------
class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    staff = relationship("User", back_populates="company", cascade="all, delete-orphan")
    drivers = relationship("Driver", back_populates="company", cascade="all, delete-orphan")


# -------- Staff User (one per dept) --------
class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("company_id", "department", name="uq_company_department"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    must_reset_password: Mapped[bool] = mapped_column(default=True)

    department: Mapped[DepartmentEnum] = mapped_column(
        SAEnum(DepartmentEnum, name="department_enum", native_enum=False), nullable=False
    )

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    company = relationship("Company", back_populates="staff")

    ratings = relationship("DriverRating", back_populates="user", cascade="all, delete-orphan")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# -------- Driver --------
class Driver(Base):
    __tablename__ = "drivers"
    __table_args__ = (
        UniqueConstraint("license_number", name="uq_driver_license"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    dob: Mapped[Date] = mapped_column(Date, nullable=False)
    license_number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    created_by_company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    company = relationship("Company", back_populates="drivers")

    ratings = relationship("DriverRating", back_populates="driver", cascade="all, delete-orphan")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# -------- Driver Rating --------
class DriverRating(Base):
    __tablename__ = "driver_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    department: Mapped[DepartmentEnum] = mapped_column(
        SAEnum(DepartmentEnum, name="department_enum", native_enum=False), nullable=False
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..5 validated in Pydantic
    comment: Mapped[str | None] = mapped_column(String(2000))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    driver = relationship("Driver", back_populates="ratings")
    user = relationship("User", back_populates="ratings")
