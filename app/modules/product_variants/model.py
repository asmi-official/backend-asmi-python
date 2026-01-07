from sqlalchemy import String, DateTime, ForeignKey, Index, Boolean, Integer, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from app.config.database import Base
import uuid as uuid_pkg

if TYPE_CHECKING:
    from app.modules.products.model import Product
    from app.modules.media.model import ProductImage
    from app.modules.inventory.model import StockMovement


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4, index=True)
    product_id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)

    # Variant Code
    variant_code: Mapped[str] = mapped_column(String(50), nullable=False, comment="VAR-0001")
    variant_sequence: Mapped[int] = mapped_column(Integer, nullable=False)

    # Variant Name (Combined attributes)
    variant_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Large / Red")

    # Pricing
    price_adjustment: Mapped[float] = mapped_column(DECIMAL(15, 2), default=0, comment="+/- dari base price")
    selling_price: Mapped[Optional[float]] = mapped_column(DECIMAL(15, 2), nullable=True, comment="Override price (optional)")

    # Inventory
    sku: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    qty: Mapped[int] = mapped_column(Integer, default=0)
    min_stock: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Physical Specs Override
    weight: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)
    length: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)
    width: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)
    height: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    updated_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="variants")
    attribute_mappings: Mapped[List["VariantAttributeMapping"]] = relationship("VariantAttributeMapping", back_populates="variant", cascade="all, delete-orphan")
    images: Mapped[List["ProductImage"]] = relationship("ProductImage", back_populates="variant", cascade="all, delete-orphan")
    stock_movements: Mapped[List["StockMovement"]] = relationship("StockMovement", back_populates="variant")

    __table_args__ = (
        Index('idx_sku_unique', 'sku', unique=True),
        Index('idx_variant_sequence', 'product_id', 'variant_sequence', unique=True),
        Index('idx_variant_name', 'product_id', 'variant_name', unique=True),
    )


class VariantAttribute(Base):
    __tablename__ = "variant_attributes"

    id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4, index=True)
    product_id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True, comment="Attributes per product")

    attribute_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Size, Color, Material, Rasa, etc")

    display_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="variant_attributes")
    values: Mapped[List["VariantAttributeValue"]] = relationship("VariantAttributeValue", back_populates="attribute", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_attribute_per_product', 'product_id', 'attribute_name', unique=True),
    )


class VariantAttributeValue(Base):
    __tablename__ = "variant_attribute_values"

    id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4, index=True)
    attribute_id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("variant_attributes.id", ondelete="CASCADE"), nullable=False, index=True)

    value: Mapped[str] = mapped_column(String(100), nullable=False, comment="Small, Red, Cotton, Vanilla, etc")

    # Visual (optional, for colors)
    color_code: Mapped[Optional[str]] = mapped_column(String(7), nullable=True, comment="#FF0000 for red")
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="Image for this option")

    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    attribute: Mapped["VariantAttribute"] = relationship("VariantAttribute", back_populates="values")
    mappings: Mapped[List["VariantAttributeMapping"]] = relationship("VariantAttributeMapping", back_populates="attribute_value", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_value_per_attribute', 'attribute_id', 'value', unique=True),
    )


class VariantAttributeMapping(Base):
    __tablename__ = "variant_attribute_mappings"

    id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4, index=True)
    variant_id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False, index=True)
    attribute_value_id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("variant_attribute_values.id", ondelete="CASCADE"), nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    variant: Mapped["ProductVariant"] = relationship("ProductVariant", back_populates="attribute_mappings")
    attribute_value: Mapped["VariantAttributeValue"] = relationship("VariantAttributeValue", back_populates="mappings")

    __table_args__ = (
        Index('idx_variant_attribute', 'variant_id', 'attribute_value_id', unique=True),
    )
