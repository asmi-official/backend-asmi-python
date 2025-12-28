from sqlalchemy import String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from app.config.database import Base
import enum
import uuid as uuid_pkg

if TYPE_CHECKING:
    from app.models.business import Business


class UserRole(enum.Enum):
    admin = "admin"
    merchant = "merchant"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    businesses: Mapped[List["Business"]] = relationship("Business", back_populates="user")

