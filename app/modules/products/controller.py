from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from fastapi import UploadFile
import json
from app.modules.products.usecase import ProductUsecase
from app.modules.products.schema import ProductCreateSchema, ProductUpdateSchema


class ProductController:

    @staticmethod
    async def create_product_with_form(
        name: str,
        product_type: str,
        base_price: float,
        selling_price: float,
        description: Optional[str],
        category_id: Optional[str],
        qty: Optional[int],
        min_stock: Optional[int],
        max_stock: Optional[int],
        weight: Optional[float],
        length: Optional[float],
        width: Optional[float],
        height: Optional[float],
        is_active: bool,
        is_featured: bool,
        track_inventory: bool,
        attributes: Optional[str],
        variants: Optional[str],
        main_images: List[UploadFile],
        variant_images: Optional[List[UploadFile]],
        business_id: UUID,
        user_id: UUID,
        created_by: str,
        db: Session
    ):
        """Handle product creation from multipart form data"""
        usecase = ProductUsecase(db)

        # Build product data dict
        data_dict = {
            "name": name,
            "product_type": product_type,
            "base_price": base_price,
            "selling_price": selling_price,
            "description": description,
            "category_id": category_id,
            "qty": qty,
            "min_stock": min_stock,
            "max_stock": max_stock,
            "weight": weight,
            "length": length,
            "width": width,
            "height": height,
            "is_active": is_active,
            "is_featured": is_featured,
            "track_inventory": track_inventory,
            "images": [],
            "attributes": json.loads(attributes) if attributes else [],
            "variants": json.loads(variants) if variants else []
        }

        # Parse to schema
        data = ProductCreateSchema(**data_dict)

        return await usecase.create_product_with_files(
            data=data,
            business_id=business_id,
            user_id=user_id,
            created_by=created_by,
            main_images=main_images,
            variant_images=variant_images or [],
            db=db
        )

    @staticmethod
    def get_product_by_id(product_id: UUID, business_id: UUID, db: Session):
        usecase = ProductUsecase(db)
        return usecase.get_product_by_id(product_id, business_id)

    @staticmethod
    def get_products_by_business(
        search: Optional[str] = None,
        filters: Optional[list] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        db: Session = None  # type: ignore
    ):
        usecase = ProductUsecase(db)
        return usecase.get_products_by_business(
            search=search,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=per_page
        )

    @staticmethod
    async def update_product_with_form(
        product_id: UUID,
        name: str,
        product_type: str,
        base_price: float,
        selling_price: float,
        description: Optional[str],
        category_id: Optional[str],
        qty: Optional[int],
        min_stock: Optional[int],
        max_stock: Optional[int],
        weight: Optional[float],
        length: Optional[float],
        width: Optional[float],
        height: Optional[float],
        is_active: bool,
        is_featured: bool,
        track_inventory: bool,
        attributes: Optional[str],
        variants: Optional[str],
        main_images: List[UploadFile],
        variant_images: Optional[List[UploadFile]],
        business_id: UUID,
        updated_by: str,
        db: Session
    ):
        """Handle product update from multipart form data (full replace)"""
        usecase = ProductUsecase(db)

        # Build product data dict
        data_dict = {
            "name": name,
            "product_type": product_type,
            "base_price": base_price,
            "selling_price": selling_price,
            "description": description,
            "category_id": category_id,
            "qty": qty,
            "min_stock": min_stock,
            "max_stock": max_stock,
            "weight": weight,
            "length": length,
            "width": width,
            "height": height,
            "is_active": is_active,
            "is_featured": is_featured,
            "track_inventory": track_inventory,
            "images": [],
            "attributes": json.loads(attributes) if attributes else [],
            "variants": json.loads(variants) if variants else []
        }

        # Parse to schema (reuse create schema for full replace)
        data = ProductCreateSchema(**data_dict)

        return await usecase.update_product_with_files(
            product_id=product_id,
            data=data,
            business_id=business_id,
            updated_by=updated_by,
            main_images=main_images,
            variant_images=variant_images or [],
            db=db
        )

    @staticmethod
    def delete_product(product_id: UUID, business_id: UUID, deleted_by: str, db: Session):
        usecase = ProductUsecase(db)
        return usecase.delete_product(product_id, business_id, deleted_by)
