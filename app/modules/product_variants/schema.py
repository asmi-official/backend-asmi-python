from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, List


# ========== Variant Attribute Schemas ==========

class VariantAttributeValueCreate(BaseModel):
    value: str = Field(..., description="Value (Small, Red, Cotton, dll)")
    color_code: Optional[str] = Field(None, max_length=7, description="Color code (#FF0000)")
    image_url: Optional[str] = Field(None, max_length=500, description="Image URL for this value")
    display_order: int = Field(default=0, description="Display order")


class VariantAttributeCreate(BaseModel):
    attribute_name: str = Field(..., max_length=100, description="Attribute name (Size, Color, dll)")
    display_order: int = Field(default=0, description="Display order")
    values: List[VariantAttributeValueCreate] = Field(..., description="List of attribute values")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "attribute_name": "Size",
                    "display_order": 0,
                    "values": [
                        {"value": "Small", "display_order": 0},
                        {"value": "Medium", "display_order": 1},
                        {"value": "Large", "display_order": 2}
                    ]
                }
            ]
        }
    )


# ========== Product Variant Schemas ==========

class VariantAttributeValueMapping(BaseModel):
    attribute_id: UUID = Field(..., description="Attribute ID")
    value_id: UUID = Field(..., description="Value ID")


class ProductVariantCreate(BaseModel):
    # Variant name will be auto-generated from attributes
    # e.g., "Large / Red" or "Medium / Blue"

    # Pricing
    price_adjustment: float = Field(
        default=0,
        description="+/- dari base price product"
    )
    selling_price: Optional[float] = Field(
        None,
        ge=0,
        description="Override selling price (optional)"
    )

    # Inventory
    sku: str = Field(..., max_length=100, description="SKU (must be unique)")
    barcode: Optional[str] = Field(None, max_length=50, description="Barcode")
    qty: int = Field(default=0, ge=0, description="Stock quantity")
    min_stock: Optional[int] = Field(None, ge=0, description="Minimum stock")

    # Physical Specs Override
    weight: Optional[float] = Field(None, ge=0, description="Weight in grams")
    length: Optional[float] = Field(None, ge=0, description="Length in cm")
    width: Optional[float] = Field(None, ge=0, description="Width in cm")
    height: Optional[float] = Field(None, ge=0, description="Height in cm")

    # Status
    is_active: bool = Field(default=True, description="Is variant active")
    is_default: bool = Field(default=False, description="Is default variant")

    # Attribute mappings
    attribute_values: List[VariantAttributeValueMapping] = Field(
        ...,
        description="List of attribute value IDs for this variant"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "price_adjustment": 10000,
                    "sku": "KMJ-BTK-001-LRG-RED",
                    "qty": 50,
                    "min_stock": 5,
                    "is_default": True,
                    "attribute_values": [
                        {"attribute_id": "uuid-size-attr", "value_id": "uuid-large-value"},
                        {"attribute_id": "uuid-color-attr", "value_id": "uuid-red-value"}
                    ]
                }
            ]
        }
    )


class ProductVariantUpdate(BaseModel):
    price_adjustment: Optional[float] = None
    selling_price: Optional[float] = Field(None, ge=0)
    sku: Optional[str] = Field(None, max_length=100)
    barcode: Optional[str] = Field(None, max_length=50)
    qty: Optional[int] = Field(None, ge=0)
    min_stock: Optional[int] = Field(None, ge=0)
    weight: Optional[float] = Field(None, ge=0)
    length: Optional[float] = Field(None, ge=0)
    width: Optional[float] = Field(None, ge=0)
    height: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


# ========== Response Schemas ==========

class VariantAttributeValueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    attribute_id: UUID
    value: str
    color_code: Optional[str] = None
    image_url: Optional[str] = None
    display_order: int
    is_active: bool
    created_at: datetime


class VariantAttributeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    attribute_name: str
    display_order: int
    created_at: datetime
    values: List[VariantAttributeValueResponse] = []


class ProductVariantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    variant_code: str
    variant_sequence: int
    variant_name: str

    price_adjustment: float
    selling_price: Optional[float] = None

    sku: str
    barcode: Optional[str] = None
    qty: int
    min_stock: Optional[int] = None

    weight: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None

    is_active: bool
    is_default: bool

    created_at: datetime
    updated_at: Optional[datetime] = None
