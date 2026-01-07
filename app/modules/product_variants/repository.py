from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from app.modules.product_variants.model import (
    ProductVariant,
    VariantAttribute,
    VariantAttributeValue,
    VariantAttributeMapping
)


class VariantAttributeRepository:

    @staticmethod
    def create_attribute(db: Session, attribute_data: dict) -> VariantAttribute:
        attribute = VariantAttribute(**attribute_data)
        db.add(attribute)
        db.flush()
        return attribute

    @staticmethod
    def create_attribute_value(db: Session, value_data: dict) -> VariantAttributeValue:
        value = VariantAttributeValue(**value_data)
        db.add(value)
        db.flush()
        return value

    @staticmethod
    def find_attributes_by_product(db: Session, product_id: UUID) -> List[VariantAttribute]:
        return db.query(VariantAttribute).filter(
            VariantAttribute.product_id == product_id
        ).order_by(VariantAttribute.display_order).all()

    @staticmethod
    def find_attribute_by_id(db: Session, attribute_id: UUID) -> Optional[VariantAttribute]:
        return db.query(VariantAttribute).filter(
            VariantAttribute.id == attribute_id
        ).first()

    @staticmethod
    def find_value_by_id(db: Session, value_id: UUID) -> Optional[VariantAttributeValue]:
        return db.query(VariantAttributeValue).filter(
            VariantAttributeValue.id == value_id
        ).first()

    @staticmethod
    def soft_delete(db: Session, attribute: VariantAttribute, deleted_by: str):
        """Soft delete a variant attribute"""
        from datetime import datetime
        attribute.deleted_at = datetime.now()
        attribute.deleted_by = deleted_by
        db.flush()
        return attribute


class ProductVariantRepository:

    @staticmethod
    def create_variant(db: Session, variant_data: dict) -> ProductVariant:
        variant = ProductVariant(**variant_data)
        db.add(variant)
        db.flush()
        return variant

    @staticmethod
    def create_attribute_mapping(db: Session, mapping_data: dict) -> VariantAttributeMapping:
        mapping = VariantAttributeMapping(**mapping_data)
        db.add(mapping)
        db.flush()
        return mapping

    @staticmethod
    def find_by_id(db: Session, variant_id: UUID) -> Optional[ProductVariant]:
        return db.query(ProductVariant).filter(
            ProductVariant.id == variant_id,
            ProductVariant.deleted_at.is_(None)
        ).first()

    @staticmethod
    def find_by_product(db: Session, product_id: UUID) -> List[ProductVariant]:
        return db.query(ProductVariant).filter(
            ProductVariant.product_id == product_id,
            ProductVariant.deleted_at.is_(None)
        ).order_by(ProductVariant.variant_sequence).all()

    @staticmethod
    def find_by_sku(db: Session, sku: str) -> Optional[ProductVariant]:
        return db.query(ProductVariant).filter(
            ProductVariant.sku == sku,
            ProductVariant.deleted_at.is_(None)
        ).first()

    @staticmethod
    def get_next_sequence(db: Session, product_id: UUID) -> int:
        """Get next variant sequence number for a product"""
        max_sequence = db.query(ProductVariant.variant_sequence).filter(
            ProductVariant.product_id == product_id
        ).order_by(ProductVariant.variant_sequence.desc()).first()

        return (max_sequence[0] + 1) if max_sequence else 1

    @staticmethod
    def update_variant(db: Session, variant: ProductVariant, update_data: dict) -> ProductVariant:
        for key, value in update_data.items():
            if value is not None:
                setattr(variant, key, value)
        db.flush()
        return variant

    @staticmethod
    def soft_delete(db: Session, variant: ProductVariant, deleted_by: str):
        from datetime import datetime
        variant.deleted_at = datetime.now()
        variant.deleted_by = deleted_by
        db.flush()
        return variant

    @staticmethod
    def delete_attribute_mappings(db: Session, variant_id: UUID):
        """Delete all attribute mappings for a variant"""
        db.query(VariantAttributeMapping).filter(
            VariantAttributeMapping.variant_id == variant_id
        ).delete()
        db.flush()
