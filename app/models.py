"""
Central import file for all models
This ensures all models are registered with SQLAlchemy's Base.metadata
"""

from app.modules.auth.model import User, UserRole  # noqa: F401
from app.modules.business.model import Business, BusinessStatus  # noqa: F401
from app.modules.master_type.model import MasterTypes  # noqa: F401
from app.modules.order_secret.model import OrderSecret  # noqa: F401
from app.modules.naming_series.model import NamingSeries  # noqa: F401

# Product-related modules (bounded contexts)
from app.modules.products.model import Product, ProductType  # noqa: F401
from app.modules.product_variants.model import (  # noqa: F401
    ProductVariant,
    VariantAttribute,
    VariantAttributeValue,
    VariantAttributeMapping
)
from app.modules.inventory.model import StockMovement, MovementType  # noqa: F401
from app.modules.media.model import ProductImage  # noqa: F401
from app.modules.marketplace.model import ProductMarketplaceListing  # noqa: F401

__all__ = [
    # Auth
    "User",
    "UserRole",
    # Business
    "Business",
    "BusinessStatus",
    # Master Data
    "MasterTypes",
    "OrderSecret",
    "NamingSeries",
    # Products (Core)
    "Product",
    "ProductType",
    # Product Variants
    "ProductVariant",
    "VariantAttribute",
    "VariantAttributeValue",
    "VariantAttributeMapping",
    # Inventory
    "StockMovement",
    "MovementType",
    # Media
    "ProductImage",
    # Marketplace
    "ProductMarketplaceListing",
]
