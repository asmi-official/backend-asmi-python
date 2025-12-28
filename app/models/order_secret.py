from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from app.config.database import Base
import uuid as uuid_pkg


class OrderSecret(Base):
    __tablename__ = "order_secrets"

    id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4, index=True)
    order_secret_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    marketplace_type_id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("master_types.id"), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    emotional: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    from_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    updated_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationship
    marketplace_type = relationship("MasterTypes")
