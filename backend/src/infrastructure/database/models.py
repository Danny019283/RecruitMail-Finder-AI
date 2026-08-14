from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Company(SQLModel, table=True):
    __tablename__ = "company"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, nullable=False)
    domain_url: str = Field(max_length=255, nullable=False, unique=True, index=True)
    description: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)

    # Relationships
    contacts: List["Contact"] = Relationship(back_populates="company", cascade_delete=True)

class Contact(SQLModel, table=True):
    __tablename__ = "contact"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, nullable=False, unique=True, index=True)
    detected_at: datetime = Field(default_factory=utc_now, nullable=False)
    id_company: int = Field(foreign_key="company.id", nullable=False)
    subdomain: str = Field(max_length=255, nullable=False)
    
    # Relationships
    company: "Company" = Relationship(back_populates="contacts")
