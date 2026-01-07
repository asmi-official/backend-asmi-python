from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.modules.product_variants.repository import ProductVariantRepository, VariantAttributeRepository
from app.modules.product_variants.schema import (
    VariantAttributeCreate,
    ProductVariantCreate,
    ProductVariantUpdate
)
from app.modules.products.repository import ProductRepository
from app.modules.products.model import ProductType
from app.core.response import SuccessResponse
from app.core.exceptions import NotFoundException, BadRequestException


class VariantAttributeUsecase:

    def __init__(self, db: Session):
        self.db = db
        self.repository = VariantAttributeRepository()
        self.product_repository = ProductRepository()

    def create_attributes(self, product_id: UUID, attributes: List[VariantAttributeCreate], created_by: str):
        """
        Create variant attributes for a product.
        This should be called before creating variants.
        """
        try:
            # 1. Validate product exists and is VARIABLE type
            product = self.product_repository.find_by_id(self.db, product_id)
            if not product:
                raise NotFoundException(
                    message="Product not found",
                    details={"product_id": str(product_id)}
                )

            if product.product_type != ProductType.VARIABLE:
                raise BadRequestException(
                    message="Product must be VARIABLE type to have attributes",
                    details={"product_type": product.product_type.value}
                )

            created_attributes = []

            for attr_data in attributes:
                # Create attribute
                attribute = self.repository.create_attribute(self.db, {
                    "product_id": product_id,
                    "attribute_name": attr_data.attribute_name,
                    "display_order": attr_data.display_order,
                    "created_by": created_by
                })

                # Create attribute values
                for value_data in attr_data.values:
                    self.repository.create_attribute_value(self.db, {
                        "attribute_id": attribute.id,
                        "value": value_data.value,
                        "color_code": value_data.color_code,
                        "image_url": value_data.image_url,
                        "display_order": value_data.display_order
                    })

                created_attributes.append(attribute)

            self.db.commit()

            # Refresh to get values
            for attr in created_attributes:
                self.db.refresh(attr)

            return SuccessResponse.created(
                message="Variant attributes created successfully",
                data=created_attributes
            )

        except Exception as e:
            self.db.rollback()
            raise e

    def get_attributes_by_product(self, product_id: UUID):
        """Get all attributes for a product"""
        # Validate product exists
        product = self.product_repository.find_by_id(self.db, product_id)
        if not product:
            raise NotFoundException(
                message="Product not found",
                details={"product_id": str(product_id)}
            )

        attributes = self.repository.find_attributes_by_product(self.db, product_id)

        return SuccessResponse.success(
            message="Variant attributes retrieved successfully",
            data=attributes
        )


class ProductVariantUsecase:

    def __init__(self, db: Session):
        self.db = db
        self.repository = ProductVariantRepository()
        self.product_repository = ProductRepository()
        self.attribute_repository = VariantAttributeRepository()

    def create_variant(self, product_id: UUID, data: ProductVariantCreate, created_by: str):
        try:
            # 1. Validate product exists and is VARIABLE type
            product = self.product_repository.find_by_id(self.db, product_id)
            if not product:
                raise NotFoundException(
                    message="Product not found",
                    details={"product_id": str(product_id)}
                )

            if product.product_type != ProductType.VARIABLE:
                raise BadRequestException(
                    message="Product must be VARIABLE type to have variants",
                    details={"product_type": product.product_type.value}
                )

            # 2. Validate SKU unique
            existing_sku = self.repository.find_by_sku(self.db, data.sku)
            if existing_sku:
                raise BadRequestException(
                    message="SKU already exists",
                    details={"sku": data.sku}
                )

            # 3. Validate attribute values exist and belong to product's attributes
            variant_name_parts = []
            for attr_mapping in data.attribute_values:
                attribute = self.attribute_repository.find_attribute_by_id(self.db, attr_mapping.attribute_id)
                if not attribute or attribute.product_id != product_id:
                    raise BadRequestException(
                        message="Invalid attribute for this product",
                        details={"attribute_id": str(attr_mapping.attribute_id)}
                    )

                value = self.attribute_repository.find_value_by_id(self.db, attr_mapping.value_id)
                if not value or value.attribute_id != attr_mapping.attribute_id:
                    raise BadRequestException(
                        message="Invalid attribute value",
                        details={"value_id": str(attr_mapping.value_id)}
                    )

                variant_name_parts.append(value.value)

            # 4. Generate variant code and name
            variant_sequence = self.repository.get_next_sequence(self.db, product_id)
            variant_code = f"{product.product_code}-VAR-{str(variant_sequence).zfill(4)}"
            variant_name = " / ".join(variant_name_parts)  # e.g., "Large / Red"

            # 5. Create variant
            variant_data = {
                "product_id": product_id,
                "variant_code": variant_code,
                "variant_sequence": variant_sequence,
                "variant_name": variant_name,
                "price_adjustment": data.price_adjustment,
                "selling_price": data.selling_price,
                "sku": data.sku,
                "barcode": data.barcode,
                "qty": data.qty,
                "min_stock": data.min_stock,
                "weight": data.weight,
                "length": data.length,
                "width": data.width,
                "height": data.height,
                "is_active": data.is_active,
                "is_default": data.is_default,
                "created_by": created_by
            }

            variant = self.repository.create_variant(self.db, variant_data)

            # 6. Create attribute mappings
            for attr_mapping in data.attribute_values:
                self.repository.create_attribute_mapping(self.db, {
                    "variant_id": variant.id,
                    "attribute_value_id": attr_mapping.value_id
                })

            # 7. Commit
            self.db.commit()
            self.db.refresh(variant)

            return SuccessResponse.created(
                message="Product variant created successfully",
                data=variant
            )

        except Exception as e:
            self.db.rollback()
            raise e

    def get_variants_by_product(self, product_id: UUID):
        """Get all variants for a product"""
        # Validate product exists
        product = self.product_repository.find_by_id(self.db, product_id)
        if not product:
            raise NotFoundException(
                message="Product not found",
                details={"product_id": str(product_id)}
            )

        variants = self.repository.find_by_product(self.db, product_id)

        return SuccessResponse.success(
            message="Product variants retrieved successfully",
            data={
                "product_id": str(product_id),
                "total": len(variants),
                "variants": variants
            }
        )

    def get_variant_by_id(self, variant_id: UUID, product_id: UUID):
        """Get a specific variant"""
        variant = self.repository.find_by_id(self.db, variant_id)
        if not variant or variant.product_id != product_id:
            raise NotFoundException(
                message="Variant not found",
                details={"variant_id": str(variant_id)}
            )

        return SuccessResponse.success(
            message="Variant retrieved successfully",
            data=variant
        )

    def update_variant(self, variant_id: UUID, product_id: UUID, data: ProductVariantUpdate, updated_by: str):
        try:
            # 1. Find variant
            variant = self.repository.find_by_id(self.db, variant_id)
            if not variant or variant.product_id != product_id:
                raise NotFoundException(
                    message="Variant not found",
                    details={"variant_id": str(variant_id)}
                )

            # 2. Validate SKU unique if being updated
            if data.sku and data.sku != variant.sku:
                existing_sku = self.repository.find_by_sku(self.db, data.sku)
                if existing_sku:
                    raise BadRequestException(
                        message="SKU already exists",
                        details={"sku": data.sku}
                    )

            # 3. Update variant
            update_data = data.model_dump(exclude_unset=True)
            update_data["updated_by"] = updated_by

            variant = self.repository.update_variant(self.db, variant, update_data)

            # 4. Commit
            self.db.commit()
            self.db.refresh(variant)

            return SuccessResponse.success(
                message="Variant updated successfully",
                data=variant
            )

        except Exception as e:
            self.db.rollback()
            raise e

    def delete_variant(self, variant_id: UUID, product_id: UUID, deleted_by: str):
        try:
            # 1. Find variant
            variant = self.repository.find_by_id(self.db, variant_id)
            if not variant or variant.product_id != product_id:
                raise NotFoundException(
                    message="Variant not found",
                    details={"variant_id": str(variant_id)}
                )

            # 2. Soft delete
            self.repository.soft_delete(self.db, variant, deleted_by)

            # 3. Commit
            self.db.commit()

            return SuccessResponse.success(
                message="Variant deleted successfully",
                data=None
            )

        except Exception as e:
            self.db.rollback()
            raise e
