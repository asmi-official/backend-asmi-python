from sqlalchemy import String, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from app.config.database import Base
import uuid as uuid_pkg


class MasterTypes(Base):
    __tablename__ = "master_types"

    id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4, index=True)
    group_code: Mapped[str] = mapped_column(String, nullable=False, index=True)  # BUSINESS, PRODUCT, ORDER, USER
    code: Mapped[str] = mapped_column(String(5), nullable=False, index=True)  # ASMI, RM, RETAIL (max 5 digit)
    name: Mapped[str] = mapped_column(String, nullable=False)  # Supplier ASMI, Rumah Makan
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Email user yang membuat
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    updated_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Email user yang update
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Email user yang menghapus

    # Partial unique index: code must be unique only for non-deleted records
    __table_args__ = (
        Index(
            'idx_master_types_code_unique_not_deleted',
            'code',
            unique=True,
            postgresql_where=deleted_at.is_(None)
        ),
    )
