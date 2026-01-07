from sqlalchemy import String, DateTime, Text, ForeignKey, Index, Boolean
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


class ProductMarketplaceListing(Base):
    __tablename__ = "product_marketplace_listings"

    id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4, index=True)

    # Product Reference
    product_id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_id: Mapped[Optional[uuid_pkg.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=True)

    # Marketplace Info
    marketplace_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True, comment="tokopedia, shopee, bukalapak, lazada, tiktok")

    # Response dari Upload
    marketplace_product_id: Mapped[str] = mapped_column(String(100), nullable=False, comment="ID dari marketplace")
    product_url: Mapped[str] = mapped_column(Text, nullable=False, comment="Link ke product page")

    # Status
    is_success: Mapped[bool] = mapped_column(Boolean, default=True, comment="Upload berhasil atau tidak")

    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship("Product")
    variant: Mapped[Optional["ProductVariant"]] = relationship("ProductVariant")

    __table_args__ = (
        Index('idx_unique_product_marketplace', 'product_id', 'variant_id', 'marketplace_type', unique=True),
    )
