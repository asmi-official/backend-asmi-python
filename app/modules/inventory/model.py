from sqlalchemy import String, DateTime, Text, ForeignKey, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from app.config.database import Base
import enum
import uuid as uuid_pkg

if TYPE_CHECKING:
    from app.modules.products.model import Product
    from app.modules.product_variants.model import ProductVariant
    from app.modules.business.model import Business


class MovementType(enum.Enum):
    IN = "IN"
    OUT = "OUT"
    ADJUSTMENT = "ADJUSTMENT"
    TRANSFER = "TRANSFER"


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4, index=True)
    product_id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    variant_id: Mapped[Optional[uuid_pkg.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=True, index=True)
    business_id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True)

    # Movement
    movement_type: Mapped[MovementType] = mapped_column(Enum(MovementType, name="movement_type"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, comment="Positive/Negative")
    qty_before: Mapped[int] = mapped_column(Integer, nullable=False)
    qty_after: Mapped[int] = mapped_column(Integer, nullable=False)

    # Reference
    reference_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="order, purchase, adjustment")
    reference_id: Mapped[Optional[uuid_pkg.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    reference_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Details
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="stock_movements")
    variant: Mapped[Optional["ProductVariant"]] = relationship("ProductVariant", back_populates="stock_movements")
    business: Mapped["Business"] = relationship("Business")
