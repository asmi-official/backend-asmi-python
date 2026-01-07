from sqlalchemy import String, DateTime, Text, ForeignKey, Index, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from app.config.database import Base
import enum
import uuid as uuid_pkg

if TYPE_CHECKING:
    from app.modules.auth.model import User
    from app.modules.products.model import Product


class BusinessStatus(enum.Enum):
    trial = "trial"
    active = "active"
    suspended = "suspended"


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4, index=True)
    business_code: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    business_name: Mapped[str] = mapped_column(String, nullable=False)
    shop_name: Mapped[str] = mapped_column(String, nullable=False)
    name_owner: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    business_type_id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("master_types.id"), nullable=False)
    status: Mapped[BusinessStatus] = mapped_column(Enum(BusinessStatus, name="business_status"), nullable=False, default=BusinessStatus.trial)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    updated_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="businesses")
    business_type = relationship("MasterTypes")
    products: Mapped[List["Product"]] = relationship("Product", back_populates="business")

    # Partial unique index: business_code must be unique only for non-deleted records
    __table_args__ = (
        Index(
            'idx_businesses_business_code_unique_not_deleted',
            'business_code',
            unique=True,
            postgresql_where=deleted_at.is_(None)
        ),
    )
