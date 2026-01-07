from sqlalchemy import String, DateTime, Text, ForeignKey, Index, Enum, Boolean, Integer, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from app.config.database import Base
import enum
import uuid as uuid_pkg

if TYPE_CHECKING:
    from app.modules.business.model import Business
    from app.modules.product_variants.model import ProductVariant, VariantAttribute
    from app.modules.media.model import ProductImage
    from app.modules.inventory.model import StockMovement


class ProductType(enum.Enum):
    SIMPLE = "SIMPLE"
    VARIABLE = "VARIABLE"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4, index=True)

    # Identification
    product_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True, comment="BIZ001-PROD-0001")
    product_sequence: Mapped[int] = mapped_column(Integer, nullable=False)

    # Ownership
    user_id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    business_id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id: Mapped[Optional[uuid_pkg.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)

    # Basic Info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Product Type
    product_type: Mapped[ProductType] = mapped_column(Enum(ProductType, name="product_type"), nullable=False, default=ProductType.SIMPLE)

    # Pricing
    base_price: Mapped[float] = mapped_column(DECIMAL(15, 2), nullable=False, comment="Cost/COGS")
    selling_price: Mapped[float] = mapped_column(DECIMAL(15, 2), nullable=False)

    # Inventory (Nullable untuk FOOD)
    track_inventory: Mapped[bool] = mapped_column(Boolean, default=True)
    qty: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    min_stock: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_stock: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # SKU & Barcode
    sku: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Physical Specs (for shipping)
    weight: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True, comment="in grams")
    length: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True, comment="in cm")
    width: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True, comment="in cm")
    height: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True, comment="in cm")

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)

    # Marketplace
    is_synced_to_marketplace: Mapped[bool] = mapped_column(Boolean, default=False)

    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    updated_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    business: Mapped["Business"] = relationship("Business", back_populates="products")
    variants: Mapped[List["ProductVariant"]] = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    variant_attributes: Mapped[List["VariantAttribute"]] = relationship("VariantAttribute", back_populates="product", cascade="all, delete-orphan")
    images: Mapped[List["ProductImage"]] = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    stock_movements: Mapped[List["StockMovement"]] = relationship("StockMovement", back_populates="product")

    __table_args__ = (
        Index('idx_product_code', 'product_code', unique=True),
        Index('idx_sequence_per_business', 'business_id', 'product_sequence', unique=True),
        Index('idx_sku_per_business', 'business_id', 'sku', unique=True),
        Index('idx_slug_per_business', 'business_id', 'slug', unique=True),
    )
