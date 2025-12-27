from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid


class CategoryMarketplace(Base):
    __tablename__ = "category_marketplaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)  # Uniqueness enforced by partial index
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=True)  # Email user yang membuat
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String, nullable=True)  # Email user yang update
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(String, nullable=True)  # Email user yang menghapus

    # Relationship
    order_secrets = relationship("OrderSecret", back_populates="category_marketplace")

    # Partial unique index: name must be unique only for non-deleted records
    __table_args__ = (
        Index(
            'idx_category_marketplaces_name_unique_not_deleted',
            'name',
            unique=True,
            postgresql_where=deleted_at.is_(None)
        ),
    )
