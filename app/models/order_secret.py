from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid


class OrderSecret(Base):
    __tablename__ = "order_secrets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    order_secret_id = Column(String, unique=True, nullable=False, index=True)
    category_marketplace_id = Column(UUID(as_uuid=True), ForeignKey("category_marketplaces.id"), nullable=False)
    message = Column(String, nullable=True)
    emotional = Column(String, nullable=True)
    from_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(String, nullable=True)

    # Relationship
    category_marketplace = relationship("CategoryMarketplace", back_populates="order_secrets")
