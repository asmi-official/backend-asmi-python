from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from app.modules.products.model import Product
from uuid import UUID


class ProductRepository:

    @staticmethod
    def create_product(db: Session, product_data: dict) -> Product:
        product = Product(**product_data)
        db.add(product)
        db.flush()
        return product

    @staticmethod
    def find_by_id(db: Session, product_id: UUID) -> Optional[Product]:
        return db.query(Product).filter(
            Product.id == product_id,
            Product.deleted_at.is_(None)
        ).first()

    @staticmethod
    def find_by_id_and_business(db: Session, product_id: UUID, business_id: UUID) -> Optional[Product]:
        from app.modules.product_variants.model import ProductVariant, VariantAttribute

        return db.query(Product).filter(
            Product.id == product_id,
            Product.business_id == business_id,
            Product.deleted_at.is_(None)
        ).options(
            joinedload(Product.images),
            joinedload(Product.variant_attributes).joinedload(VariantAttribute.values),
            joinedload(Product.variants).joinedload(ProductVariant.images),
            joinedload(Product.variants).joinedload(ProductVariant.attribute_mappings)
        ).first()

    @staticmethod
    def find_by_product_code(db: Session, product_code: str) -> Optional[Product]:
        return db.query(Product).filter(
            Product.product_code == product_code,
            Product.deleted_at.is_(None)
        ).first()

    @staticmethod
    def find_by_sku(db: Session, sku: str, business_id: UUID) -> Optional[Product]:
        return db.query(Product).filter(
            Product.sku == sku,
            Product.business_id == business_id,
            Product.deleted_at.is_(None)
        ).first()

    @staticmethod
    def find_all_by_business(db: Session, business_id: UUID, skip: int = 0, limit: int = 100) -> List[Product]:
        return db.query(Product).filter(
            Product.business_id == business_id,
            Product.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def count_by_business(db: Session, business_id: UUID) -> int:
        return db.query(Product).filter(
            Product.business_id == business_id,
            Product.deleted_at.is_(None)
        ).count()

    @staticmethod
    def get_next_sequence(db: Session, business_id: UUID) -> int:
        """Get next product sequence number for a business"""
        max_sequence = db.query(Product.product_sequence).filter(
            Product.business_id == business_id
        ).order_by(Product.product_sequence.desc()).first()

        return (max_sequence[0] + 1) if max_sequence else 1

    @staticmethod
    def update_product(db: Session, product: Product, update_data: dict) -> Product:
        for key, value in update_data.items():
            if value is not None:
                setattr(product, key, value)
        db.flush()
        return product

    @staticmethod
    def soft_delete(db: Session, product: Product, deleted_by: str):
        from datetime import datetime
        product.deleted_at = datetime.now()
        product.deleted_by = deleted_by
        db.flush()
        return product
