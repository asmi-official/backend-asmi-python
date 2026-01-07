from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum
from uuid import UUID
from typing import Optional, List


class ProductTypeEnum(str, Enum):
    SIMPLE = "SIMPLE"
    VARIABLE = "VARIABLE"


# ========== Nested Schemas for Creation ==========

class AttributeValueCreate(BaseModel):
    value: str
    color_code: Optional[str] = None
    image_url: Optional[str] = None
    display_order: int = 0


class AttributeCreate(BaseModel):
    attribute_name: str
    display_order: int = 0
    values: List[AttributeValueCreate]


class ProductImageCreate(BaseModel):
    image_url: str
    image_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    display_order: int = 0
    is_primary: bool = False
    alt_text: Optional[str] = None


class VariantCreate(BaseModel):
    """
    For VARIABLE products.
    attribute_value_names will be matched to created attributes.
    Example: {"Size": "Large", "Color": "Red"}
    """
    attribute_values: dict[str, str] = Field(
        ...,
        description="Map of attribute_name to value_name",
        examples=[{"Size": "Large", "Color": "Red"}]
    )
    price_adjustment: float = 0
    selling_price: Optional[float] = None
    qty: int = 0
    min_stock: Optional[int] = None
    weight: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    is_active: bool = True
    is_default: bool = False
    images: List[ProductImageCreate] = []


# ========== Main Product Schemas ==========

class ProductCreateSchema(BaseModel):
    # Basic Info
    name: str = Field(..., description="Nama produk")
    description: Optional[str] = None
    category_id: Optional[UUID] = None

    # Product Type
    product_type: ProductTypeEnum = ProductTypeEnum.SIMPLE

    # Pricing
    base_price: float = Field(..., ge=0)
    selling_price: float = Field(..., ge=0)

    # Inventory (for SIMPLE products)
    track_inventory: bool = True
    qty: Optional[int] = Field(None, ge=0)
    min_stock: Optional[int] = Field(None, ge=0)
    max_stock: Optional[int] = Field(None, ge=0)

    # Physical Specs
    weight: Optional[float] = Field(None, ge=0)
    length: Optional[float] = Field(None, ge=0)
    width: Optional[float] = Field(None, ge=0)
    height: Optional[float] = Field(None, ge=0)

    # Status
    is_active: bool = True
    is_featured: bool = False

    # Nested Creation
    images: List[ProductImageCreate] = []
    attributes: List[AttributeCreate] = []  # For VARIABLE products
    variants: List[VariantCreate] = []  # For VARIABLE products

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Kemeja Batik Premium",
                    "description": "Kemeja batik dengan varian ukuran dan warna",
                    "product_type": "VARIABLE",
                    "base_price": 100000,
                    "selling_price": 150000,
                    "weight": 250,
                    "images": [
                        {
                            "image_url": "https://cdn.example.com/kemeja-1.jpg",
                            "image_path": "/uploads/kemeja-1.jpg",
                            "is_primary": True
                        }
                    ],
                    "attributes": [
                        {
                            "attribute_name": "Size",
                            "values": [
                                {"value": "S"},
                                {"value": "M"},
                                {"value": "L"}
                            ]
                        },
                        {
                            "attribute_name": "Color",
                            "values": [
                                {"value": "Red", "color_code": "#FF0000"},
                                {"value": "Blue", "color_code": "#0000FF"}
                            ]
                        }
                    ],
                    "variants": [
                        {
                            "attribute_values": {"Size": "L", "Color": "Red"},
                            "qty": 50,
                            "price_adjustment": 0,
                            "is_default": True
                        },
                        {
                            "attribute_values": {"Size": "M", "Color": "Blue"},
                            "qty": 30,
                            "price_adjustment": -5000
                        }
                    ]
                }
            ]
        }
    )


class ProductUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    base_price: Optional[float] = Field(None, ge=0)
    selling_price: Optional[float] = Field(None, ge=0)
    track_inventory: Optional[bool] = None
    qty: Optional[int] = Field(None, ge=0)
    min_stock: Optional[int] = Field(None, ge=0)
    max_stock: Optional[int] = Field(None, ge=0)
    weight: Optional[float] = Field(None, ge=0)
    length: Optional[float] = Field(None, ge=0)
    width: Optional[float] = Field(None, ge=0)
    height: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


# ========== Response Schemas ==========

class AttributeValueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    value: str
    color_code: Optional[str] = None
    image_url: Optional[str] = None
    display_order: int


class AttributeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    attribute_name: str
    display_order: int
    values: List[AttributeValueResponse] = []


class ProductImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    image_url: str
    image_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    display_order: int
    is_primary: bool
    alt_text: Optional[str] = None


class VariantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    variant_code: str
    variant_name: str
    price_adjustment: float
    selling_price: Optional[float] = None
    sku: str
    qty: int
    min_stock: Optional[int] = None
    weight: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    is_active: bool
    is_default: bool
    images: List[ProductImageResponse] = []


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_code: str
    product_sequence: int
    user_id: UUID
    business_id: UUID
    category_id: Optional[UUID] = None

    name: str
    slug: str
    description: Optional[str] = None
    product_type: ProductTypeEnum

    base_price: float
    selling_price: float

    track_inventory: bool
    qty: Optional[int] = None
    min_stock: Optional[int] = None
    max_stock: Optional[int] = None

    sku: Optional[str] = None

    weight: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None

    is_active: bool
    is_featured: bool
    is_synced_to_marketplace: bool

    created_at: datetime
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None

    # Relations
    images: List[ProductImageResponse] = []
    attributes: List[AttributeResponse] = []
    variants: List[VariantResponse] = []
