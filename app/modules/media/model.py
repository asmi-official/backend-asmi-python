from sqlalchemy import String, DateTime, ForeignKey, Index, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from app.config.database import Base
import uuid as uuid_pkg

if TYPE_CHECKING:
    from app.modules.products.model import Product
    from app.modules.product_variants.model import ProductVariant


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4, index=True)
    product_id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_id: Mapped[Optional[uuid_pkg.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=True, index=True, comment="NULL = main product image")

    # Image Info
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)

    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="bytes")
    mime_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Display
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    alt_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="images")
    variant: Mapped[Optional["ProductVariant"]] = relationship("ProductVariant", back_populates="images")

    __table_args__ = (
        Index('idx_primary_per_product', 'product_id', 'is_primary'),
    )
