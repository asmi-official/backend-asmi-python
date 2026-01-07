from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from uuid import UUID
from app.modules.media.model import ProductImage


class ProductImageRepository:
    """Repository for ProductImage operations"""

    def create_image(self, db: Session, data: Dict[str, Any]) -> ProductImage:
        """
        Create a new product image

        Args:
            db: Database session
            data: Dict containing image data

        Returns:
            Created ProductImage object
        """
        image = ProductImage(**data)
        db.add(image)
        db.flush()  # Flush to get the ID without committing
        return image

    def create_images_bulk(self, db: Session, images_data: List[Dict[str, Any]]) -> List[ProductImage]:
        """
        Create multiple product images in bulk

        Args:
            db: Database session
            images_data: List of dicts containing image data

        Returns:
            List of created ProductImage objects
        """
        images = [ProductImage(**data) for data in images_data]
        db.add_all(images)
        db.flush()
        return images

    def find_by_id(self, db: Session, image_id: UUID) -> Optional[ProductImage]:
        """Find image by ID"""
        return db.query(ProductImage).filter(ProductImage.id == image_id).first()

    def find_by_product_id(self, db: Session, product_id: UUID) -> List[ProductImage]:
        """Get all images for a product (main product images only)"""
        return db.query(ProductImage).filter(
            ProductImage.product_id == product_id,
            ProductImage.variant_id.is_(None),
            ProductImage.deleted_at.is_(None)
        ).order_by(ProductImage.display_order).all()

    def find_by_variant_id(self, db: Session, variant_id: UUID) -> List[ProductImage]:
        """Get all images for a specific variant"""
        return db.query(ProductImage).filter(
            ProductImage.variant_id == variant_id,
            ProductImage.deleted_at.is_(None)
        ).order_by(ProductImage.display_order).all()

    def find_primary_by_product(self, db: Session, product_id: UUID) -> Optional[ProductImage]:
        """Get primary image for a product"""
        return db.query(ProductImage).filter(
            ProductImage.product_id == product_id,
            ProductImage.variant_id.is_(None),
            ProductImage.is_primary == True,
            ProductImage.deleted_at.is_(None)
        ).first()

    def find_primary_by_variant(self, db: Session, variant_id: UUID) -> Optional[ProductImage]:
        """Get primary image for a variant"""
        return db.query(ProductImage).filter(
            ProductImage.variant_id == variant_id,
            ProductImage.is_primary == True,
            ProductImage.deleted_at.is_(None)
        ).first()

    def update_image(self, db: Session, image: ProductImage, data: Dict[str, Any]) -> ProductImage:
        """Update image data"""
        for key, value in data.items():
            setattr(image, key, value)
        db.flush()
        return image

    def soft_delete(self, db: Session, image: ProductImage, deleted_by: str) -> None:
        """Soft delete an image"""
        from datetime import datetime
        image.deleted_at = datetime.utcnow()
        image.deleted_by = deleted_by
        db.flush()

    def delete_by_product(self, db: Session, product_id: UUID, deleted_by: str) -> None:
        """Soft delete all images for a product"""
        from datetime import datetime
        db.query(ProductImage).filter(
            ProductImage.product_id == product_id
        ).update({
            "deleted_at": datetime.utcnow(),
            "deleted_by": deleted_by
        })
        db.flush()

    def delete_by_variant(self, db: Session, variant_id: UUID, deleted_by: str) -> None:
        """Soft delete all images for a variant"""
        from datetime import datetime
        db.query(ProductImage).filter(
            ProductImage.variant_id == variant_id
        ).update({
            "deleted_at": datetime.utcnow(),
            "deleted_by": deleted_by
        })
        db.flush()
