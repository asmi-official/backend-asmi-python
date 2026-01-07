from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from uuid import UUID
from slugify import slugify as create_slug  # type: ignore
from fastapi import UploadFile
import uuid as uuid_pkg
import aiofiles  # type: ignore
from pathlib import Path
from app.modules.products.repository import ProductRepository
from app.modules.products.schema import ProductCreateSchema, ProductUpdateSchema, ProductImageCreate
from app.modules.products.model import ProductType, Product
from app.modules.business.repository import BusinessRepository
from app.modules.product_variants.repository import VariantAttributeRepository, ProductVariantRepository
from app.modules.product_variants.model import ProductVariant, VariantAttribute
from app.modules.media.repository import ProductImageRepository
from app.modules.naming_series import get_next_code
from app.core.response import SuccessResponse
from app.core.exceptions import NotFoundException, BadRequestException


class ProductUsecase:

    def __init__(self, db: Session):
        self.db = db
        self.repository = ProductRepository()
        self.business_repository = BusinessRepository()
        self.attribute_repository = VariantAttributeRepository()
        self.variant_repository = ProductVariantRepository()
        self.image_repository = ProductImageRepository()
        self.upload_dir = Path("images")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _delete_physical_file(self, image_path: str) -> None:
        """Delete physical file from disk"""
        try:
            file_path = Path(image_path)
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            # Log error but don't raise - file might already be deleted
            print(f"Warning: Could not delete file {image_path}: {str(e)}")

    async def _save_upload_file(self, file: UploadFile) -> Dict[str, Any]:
        """Save uploaded file and return file info"""
        # Generate unique filename
        filename = file.filename or "unknown"
        file_ext = Path(filename).suffix
        unique_filename = f"{uuid_pkg.uuid4()}{file_ext}"
        file_path = self.upload_dir / unique_filename

        # Save file
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        # Get file size
        file_size = len(content)

        return {
            "image_url": f"/images/{unique_filename}",  # URL untuk access
            "image_path": f"images/{unique_filename}",  # Relative path
            "file_size": file_size,
            "mime_type": file.content_type,
            "filename": file.filename
        }

    async def create_product_with_files(
        self,
        data: ProductCreateSchema,
        business_id: UUID,
        user_id: UUID,
        created_by: str,
        main_images: List[UploadFile],
        variant_images: List[UploadFile],
        db: Session
    ):
        """
        Create product with file uploads.
        This method handles file upload and then calls the regular create_product.
        """
        try:
            # Validate: At least 1 main image is required
            if not main_images or len(main_images) == 0:
                raise ValueError("At least 1 product image is required")

            # 1. Upload main product images
            uploaded_main_images = []
            for idx, img_file in enumerate(main_images):
                file_info = await self._save_upload_file(img_file)
                uploaded_main_images.append(ProductImageCreate(
                    image_url=file_info["image_url"],
                    image_path=file_info["image_path"],
                    file_size=file_info["file_size"],
                    mime_type=file_info["mime_type"],
                    display_order=idx,
                    is_primary=(idx == 0),  # First image is primary
                    alt_text=data.name
                ))

            # 2. Parse variant images by index (variant_0_image_0.jpg, variant_1_image_0.jpg, etc)
            variant_images_map = {}  # {variant_index: [images]}
            for img_file in variant_images:
                # Extract variant index from filename pattern: variant_{idx}_*
                try:
                    filename = img_file.filename or ""
                    if filename.startswith("variant_"):
                        parts = filename.split("_")
                        variant_idx = int(parts[1])  # Get index from variant_1_image_0.jpg

                        file_info = await self._save_upload_file(img_file)

                        if variant_idx not in variant_images_map:
                            variant_images_map[variant_idx] = []

                        variant_images_map[variant_idx].append(ProductImageCreate(
                            image_url=file_info["image_url"],
                            image_path=file_info["image_path"],
                            file_size=file_info["file_size"],
                            mime_type=file_info["mime_type"],
                            display_order=len(variant_images_map[variant_idx]),
                            is_primary=(len(variant_images_map[variant_idx]) == 0),
                            alt_text=f"{data.name} variant"
                        ))
                except (ValueError, IndexError):
                    # Skip files that don't match pattern
                    continue

            # 3. Update data with uploaded images
            data.images = uploaded_main_images

            # Update variant images
            for idx, variant in enumerate(data.variants):
                if idx in variant_images_map:
                    variant.images = variant_images_map[idx]

            # 4. Call regular create_product method
            return self.create_product(data, business_id, user_id, created_by)

        except Exception as e:
            # Cleanup uploaded files on error
            # TODO: Implement cleanup
            raise e

    def create_product(self, data: ProductCreateSchema, business_id: UUID, user_id: UUID, created_by: str):
        """
        Atomic product creation with nested attributes, variants, and images.
        All in 1 transaction with BULK INSERT operations for better performance!
        """
        try:
            # 1. Validate business exists
            business = self.business_repository.find_by_id(self.db, str(business_id))
            if not business:
                raise NotFoundException(
                    message="Business not found",
                    details={"business_id": str(business_id)}
                )

            # 2. Validate product type consistency
            if data.product_type == ProductType.VARIABLE:
                if not data.attributes or not data.variants:
                    raise BadRequestException(
                        message="VARIABLE product must have attributes and variants",
                        details={"product_type": "VARIABLE"}
                    )
            elif data.product_type == ProductType.SIMPLE:
                if data.attributes or data.variants:
                    raise BadRequestException(
                        message="SIMPLE product cannot have attributes or variants",
                        details={"product_type": "SIMPLE"}
                    )

            # 3. Generate product code
            business_code = business.business_code
            product_sequence = self.repository.get_next_sequence(self.db, business_id)
            product_code = f"{business_code}-PROD-{str(product_sequence).zfill(4)}"

            # 4. Generate SKU for SIMPLE products (auto-generated from product_code)
            product_sku = None
            if data.product_type == ProductType.SIMPLE:
                product_sku = f"SKU-{product_code}"

            # 5. Generate slug
            slug = create_slug(data.name)

            # 6. Create product
            product_data = {
                "product_code": product_code,
                "product_sequence": product_sequence,
                "user_id": user_id,
                "business_id": business_id,
                "name": data.name,
                "slug": slug,
                "description": data.description,
                "category_id": data.category_id,
                "product_type": data.product_type,
                "base_price": data.base_price,
                "selling_price": data.selling_price,
                "track_inventory": data.track_inventory,
                "qty": data.qty if data.product_type == ProductType.SIMPLE else None,
                "min_stock": data.min_stock,
                "max_stock": data.max_stock,
                "sku": product_sku,  # Auto-generated for SIMPLE, None for VARIABLE
                "weight": data.weight,
                "length": data.length,
                "width": data.width,
                "height": data.height,
                "is_active": data.is_active,
                "is_featured": data.is_featured,
                "created_by": created_by
            }

            product = self.repository.create_product(self.db, product_data)

            # 7. BULK INSERT: Prepare all product images
            if data.images:
                product_images_data = [
                    {
                        "product_id": product.id,
                        "variant_id": None,
                        "image_url": img_data.image_url,
                        "image_path": img_data.image_path,
                        "file_size": img_data.file_size,
                        "mime_type": img_data.mime_type,
                        "display_order": img_data.display_order,
                        "is_primary": img_data.is_primary,
                        "alt_text": img_data.alt_text,
                        "created_by": created_by
                    }
                    for img_data in data.images
                ]
                self.image_repository.bulk_create_images(self.db, product_images_data)

            # 8. Create attributes and variants (for VARIABLE products only)
            if data.product_type == ProductType.VARIABLE:
                # BULK INSERT: Prepare all attributes
                attributes_to_create = [
                    {
                        "product_id": product.id,
                        "attribute_name": attr_data.attribute_name,
                        "display_order": attr_data.display_order,
                        "created_by": created_by
                    }
                    for attr_data in data.attributes
                ]
                created_attributes = self.attribute_repository.bulk_create_attributes(self.db, attributes_to_create)

                # Build attribute map and prepare attribute values
                attribute_map = {}  # {attribute_name: {value_name: value_id}}
                all_attribute_values = []

                for idx, attr_data in enumerate(data.attributes):
                    attribute_id = created_attributes[idx].id
                    attribute_map[attr_data.attribute_name] = {}

                    for val_data in attr_data.values:
                        all_attribute_values.append({
                            "attribute_id": attribute_id,
                            "value": val_data.value,
                            "color_code": val_data.color_code,
                            "image_url": val_data.image_url,
                            "display_order": val_data.display_order,
                            "_temp_attr_name": attr_data.attribute_name,  # Temporary for mapping
                            "_temp_value_name": val_data.value
                        })

                # BULK INSERT: Create all attribute values at once
                if all_attribute_values:
                    created_values = self.attribute_repository.bulk_create_attribute_values(self.db, all_attribute_values)

                    # Build the value map
                    for value_obj, value_data in zip(created_values, all_attribute_values):
                        attr_name = value_data["_temp_attr_name"]
                        value_name = value_data["_temp_value_name"]
                        attribute_map[attr_name][value_name] = value_obj.id

                # Prepare variants data
                variants_to_create = []
                variant_mappings = []  # Store mappings to create after variants
                variant_images_data = []  # Store images to create after variants

                for idx, variant_data in enumerate(data.variants, start=1):
                    # Build variant name from attribute values
                    variant_name_parts = []
                    attribute_value_ids = []

                    for attr_name, value_name in variant_data.attribute_values.items():
                        if attr_name not in attribute_map:
                            raise BadRequestException(
                                message=f"Attribute '{attr_name}' not found in product attributes",
                                details={"attribute": attr_name}
                            )

                        if value_name not in attribute_map[attr_name]:
                            raise BadRequestException(
                                message=f"Value '{value_name}' not found in attribute '{attr_name}'",
                                details={"attribute": attr_name, "value": value_name}
                            )

                        variant_name_parts.append(value_name)
                        attribute_value_ids.append(attribute_map[attr_name][value_name])

                    variant_name = " / ".join(variant_name_parts)
                    variant_code = f"{product_code}-VAR-{str(idx).zfill(4)}"
                    variant_sku = f"SKU-{variant_code}"

                    variants_to_create.append({
                        "product_id": product.id,
                        "variant_code": variant_code,
                        "variant_sequence": idx,
                        "variant_name": variant_name,
                        "price_adjustment": variant_data.price_adjustment,
                        "selling_price": variant_data.selling_price,
                        "sku": variant_sku,
                        "qty": variant_data.qty,
                        "min_stock": variant_data.min_stock,
                        "weight": variant_data.weight,
                        "length": variant_data.length,
                        "width": variant_data.width,
                        "height": variant_data.height,
                        "is_active": variant_data.is_active,
                        "is_default": variant_data.is_default,
                        "created_by": created_by,
                        "_temp_attribute_value_ids": attribute_value_ids,  # Temporary
                        "_temp_images": variant_data.images  # Temporary
                    })

                # BULK INSERT: Create all variants
                if variants_to_create:
                    created_variants = self.variant_repository.bulk_create_variants(self.db, variants_to_create)

                    # Prepare variant attribute mappings and images
                    for variant_obj, variant_data in zip(created_variants, variants_to_create):
                        # Prepare attribute mappings
                        for value_id in variant_data["_temp_attribute_value_ids"]:
                            variant_mappings.append({
                                "variant_id": variant_obj.id,
                                "attribute_value_id": value_id
                            })

                        # Prepare variant images
                        for img_data in variant_data["_temp_images"]:
                            variant_images_data.append({
                                "product_id": product.id,
                                "variant_id": variant_obj.id,
                                "image_url": img_data.image_url,
                                "image_path": img_data.image_path,
                                "file_size": img_data.file_size,
                                "mime_type": img_data.mime_type,
                                "display_order": img_data.display_order,
                                "is_primary": img_data.is_primary,
                                "alt_text": img_data.alt_text,
                                "created_by": created_by
                            })

                    # BULK INSERT: Create all variant attribute mappings
                    if variant_mappings:
                        self.variant_repository.bulk_create_attribute_mappings(self.db, variant_mappings)

                    # BULK INSERT: Create all variant images
                    if variant_images_data:
                        self.image_repository.bulk_create_images(self.db, variant_images_data)

            # 9. Commit transaction
            self.db.commit()
            self.db.refresh(product)

            return SuccessResponse.created(
                message="Product created successfully",
                data=product
            )

        except Exception as e:
            self.db.rollback()
            raise e

    def get_product_by_id(self, product_id: UUID, business_id: UUID):
        product = self.repository.find_by_id_and_business(self.db, product_id, business_id)
        if not product:
            raise NotFoundException(
                message="Product not found",
                details={"product_id": str(product_id)}
            )

        return SuccessResponse.success(
            message="Product retrieved successfully",
            data=product
        )

    def get_products_by_business(
        self,
        search: Optional[str] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        page: Optional[int] = None,
        per_page: Optional[int] = None
    ):
        """
        Get products with all related data (images, variants, variant images, attributes)
        Uses dynamic query builder with pagination and filtering support.
        """
        from app.utils.query_builder import build_dynamic_query, calculate_pagination_meta
        from sqlalchemy.orm import joinedload

        # Build query with eager loading for all relationships
        query = build_dynamic_query(
            db=self.db,
            model=Product,
            search=search,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            default_sort_field="created_at",
            auto_search_all_fields=True,
            page=page,
            per_page=per_page
        )

        # Eager load all relationships to avoid N+1 queries
        query = query.options(
            joinedload(Product.images),
            joinedload(Product.variant_attributes).joinedload(VariantAttribute.values),
            joinedload(Product.variants).joinedload(ProductVariant.images),
            joinedload(Product.variants).joinedload(ProductVariant.attribute_mappings)
        )

        # Calculate pagination if requested
        if page is not None and per_page is not None:
            count_query = build_dynamic_query(
                db=self.db,
                model=Product,
                search=search,
                filters=filters,
                auto_search_all_fields=True
            )
            total = count_query.count()
            pagination_meta = calculate_pagination_meta(total, page, per_page)
        else:
            pagination_meta = None

        products = query.all()

        return SuccessResponse.retrieved(
            message="Products retrieved successfully",
            data=products,
            meta=pagination_meta
        )

    async def update_product_with_files(
        self,
        product_id: UUID,
        data: ProductCreateSchema,  # Reuse create schema for full replace
        business_id: UUID,
        updated_by: str,
        main_images: List[UploadFile],
        variant_images: List[UploadFile],
        db: Session
    ):
        """
        Full replace update: Delete old nested data and create new ones.
        Handles images, variants, and attributes atomically.
        """
        try:
            # Validate: At least 1 main image is required
            if not main_images or len(main_images) == 0:
                raise ValueError("At least 1 product image is required")

            # 1. Find existing product
            product = self.repository.find_by_id_and_business(self.db, product_id, business_id)
            if not product:
                raise NotFoundException(
                    message="Product not found",
                    details={"product_id": str(product_id)}
                )

            # 2. Validate product type consistency
            if data.product_type == ProductType.VARIABLE:
                if not data.attributes or not data.variants:
                    raise BadRequestException(
                        message="VARIABLE product must have attributes and variants",
                        details={"product_type": "VARIABLE"}
                    )
            elif data.product_type == ProductType.SIMPLE:
                if data.attributes or data.variants:
                    raise BadRequestException(
                        message="SIMPLE product cannot have attributes or variants",
                        details={"product_type": "SIMPLE"}
                    )

            # 3. Upload new images
            uploaded_main_images = []
            for idx, img_file in enumerate(main_images):
                file_info = await self._save_upload_file(img_file)
                uploaded_main_images.append(ProductImageCreate(
                    image_url=file_info["image_url"],
                    image_path=file_info["image_path"],
                    file_size=file_info["file_size"],
                    mime_type=file_info["mime_type"],
                    display_order=idx,
                    is_primary=(idx == 0),
                    alt_text=data.name
                ))

            # 4. Parse variant images
            variant_images_map = {}
            for img_file in variant_images:
                try:
                    filename = img_file.filename or ""
                    if filename.startswith("variant_"):
                        parts = filename.split("_")
                        variant_idx = int(parts[1])
                        file_info = await self._save_upload_file(img_file)

                        if variant_idx not in variant_images_map:
                            variant_images_map[variant_idx] = []

                        variant_images_map[variant_idx].append(ProductImageCreate(
                            image_url=file_info["image_url"],
                            image_path=file_info["image_path"],
                            file_size=file_info["file_size"],
                            mime_type=file_info["mime_type"],
                            display_order=len(variant_images_map[variant_idx]),
                            is_primary=(len(variant_images_map[variant_idx]) == 0),
                            alt_text=f"{data.name} variant"
                        ))
                except (ValueError, IndexError):
                    continue

            # 5. Delete old images (files + DB)
            old_images = self.image_repository.find_by_product_id(self.db, product_id)
            for old_img in old_images:
                self._delete_physical_file(old_img.image_path)
                self.image_repository.soft_delete(self.db, old_img, updated_by)

            # 6. Delete old variants (cascade will handle images and mappings)
            if product.product_type == ProductType.VARIABLE:
                # Get all variant images for deletion
                for variant in product.variants:
                    variant_images_to_delete = self.image_repository.find_by_variant_id(self.db, variant.id)
                    for v_img in variant_images_to_delete:
                        self._delete_physical_file(v_img.image_path)
                    self.variant_repository.soft_delete(self.db, variant, updated_by)

                # Delete old attributes (cascade will handle values)
                for attribute in product.variant_attributes:
                    self.attribute_repository.soft_delete(self.db, attribute, updated_by)

            # 7. Update product basic data
            product_update_data = {
                "name": data.name,
                "slug": create_slug(data.name),
                "description": data.description,
                "category_id": data.category_id,
                "product_type": data.product_type,
                "base_price": data.base_price,
                "selling_price": data.selling_price,
                "track_inventory": data.track_inventory,
                "qty": data.qty if data.product_type == ProductType.SIMPLE else None,
                "min_stock": data.min_stock,
                "max_stock": data.max_stock,
                "weight": data.weight,
                "length": data.length,
                "width": data.width,
                "height": data.height,
                "is_active": data.is_active,
                "is_featured": data.is_featured,
                "updated_by": updated_by
            }
            # SKU, product_code, product_sequence TIDAK boleh diubah

            product = self.repository.update_product(self.db, product, product_update_data)

            # 8. BULK INSERT: Create new product images
            if uploaded_main_images:
                product_images_data = [
                    {
                        "product_id": product.id,
                        "variant_id": None,
                        "image_url": img_data.image_url,
                        "image_path": img_data.image_path,
                        "file_size": img_data.file_size,
                        "mime_type": img_data.mime_type,
                        "display_order": img_data.display_order,
                        "is_primary": img_data.is_primary,
                        "alt_text": img_data.alt_text,
                        "created_by": updated_by
                    }
                    for img_data in uploaded_main_images
                ]
                self.image_repository.bulk_create_images(self.db, product_images_data)

            # 9. Create new attributes and variants (for VARIABLE products)
            if data.product_type == ProductType.VARIABLE:
                # BULK INSERT: Prepare all attributes
                attributes_to_create = [
                    {
                        "product_id": product.id,
                        "attribute_name": attr_data.attribute_name,
                        "display_order": attr_data.display_order,
                        "created_by": updated_by
                    }
                    for attr_data in data.attributes
                ]
                created_attributes = self.attribute_repository.bulk_create_attributes(self.db, attributes_to_create)

                # Build attribute map and prepare attribute values
                attribute_map = {}
                all_attribute_values = []

                for idx, attr_data in enumerate(data.attributes):
                    attribute_id = created_attributes[idx].id
                    attribute_map[attr_data.attribute_name] = {}

                    for val_data in attr_data.values:
                        all_attribute_values.append({
                            "attribute_id": attribute_id,
                            "value": val_data.value,
                            "color_code": val_data.color_code,
                            "image_url": val_data.image_url,
                            "display_order": val_data.display_order,
                            "_temp_attr_name": attr_data.attribute_name,
                            "_temp_value_name": val_data.value
                        })

                # BULK INSERT: Create all attribute values at once
                if all_attribute_values:
                    created_values = self.attribute_repository.bulk_create_attribute_values(self.db, all_attribute_values)

                    # Build the value map
                    for value_obj, value_data in zip(created_values, all_attribute_values):
                        attr_name = value_data["_temp_attr_name"]
                        value_name = value_data["_temp_value_name"]
                        attribute_map[attr_name][value_name] = value_obj.id

                # Prepare variants data
                variants_to_create = []
                variant_mappings = []
                variant_images_data = []

                for idx, variant_data in enumerate(data.variants, start=1):
                    variant_name_parts = []
                    attribute_value_ids = []

                    for attr_name, value_name in variant_data.attribute_values.items():
                        if attr_name not in attribute_map:
                            raise BadRequestException(
                                message=f"Attribute '{attr_name}' not found in product attributes",
                                details={"attribute": attr_name}
                            )

                        if value_name not in attribute_map[attr_name]:
                            raise BadRequestException(
                                message=f"Value '{value_name}' not found in attribute '{attr_name}'",
                                details={"attribute": attr_name, "value": value_name}
                            )

                        variant_name_parts.append(value_name)
                        attribute_value_ids.append(attribute_map[attr_name][value_name])

                    variant_name = " / ".join(variant_name_parts)
                    variant_code = f"{product.product_code}-VAR-{str(idx).zfill(4)}"
                    variant_sku = f"SKU-{variant_code}"

                    variants_to_create.append({
                        "product_id": product.id,
                        "variant_code": variant_code,
                        "variant_sequence": idx,
                        "variant_name": variant_name,
                        "price_adjustment": variant_data.price_adjustment,
                        "selling_price": variant_data.selling_price,
                        "sku": variant_sku,
                        "qty": variant_data.qty,
                        "min_stock": variant_data.min_stock,
                        "weight": variant_data.weight,
                        "length": variant_data.length,
                        "width": variant_data.width,
                        "height": variant_data.height,
                        "is_active": variant_data.is_active,
                        "is_default": variant_data.is_default,
                        "created_by": updated_by,
                        "_temp_attribute_value_ids": attribute_value_ids,
                        "_temp_variant_idx": idx - 1  # For image mapping
                    })

                # BULK INSERT: Create all variants
                if variants_to_create:
                    created_variants = self.variant_repository.bulk_create_variants(self.db, variants_to_create)

                    # Prepare variant attribute mappings and images
                    for variant_obj, variant_data in zip(created_variants, variants_to_create):
                        # Prepare attribute mappings
                        for value_id in variant_data["_temp_attribute_value_ids"]:
                            variant_mappings.append({
                                "variant_id": variant_obj.id,
                                "attribute_value_id": value_id
                            })

                        # Prepare variant images
                        variant_idx = variant_data["_temp_variant_idx"]
                        if variant_idx in variant_images_map:
                            for img_data in variant_images_map[variant_idx]:
                                variant_images_data.append({
                                    "product_id": product.id,
                                    "variant_id": variant_obj.id,
                                    "image_url": img_data.image_url,
                                    "image_path": img_data.image_path,
                                    "file_size": img_data.file_size,
                                    "mime_type": img_data.mime_type,
                                    "display_order": img_data.display_order,
                                    "is_primary": img_data.is_primary,
                                    "alt_text": img_data.alt_text,
                                    "created_by": updated_by
                                })

                    # BULK INSERT: Create all variant attribute mappings
                    if variant_mappings:
                        self.variant_repository.bulk_create_attribute_mappings(self.db, variant_mappings)

                    # BULK INSERT: Create all variant images
                    if variant_images_data:
                        self.image_repository.bulk_create_images(self.db, variant_images_data)

            # 10. Commit transaction
            self.db.commit()
            self.db.refresh(product)

            return SuccessResponse.success(
                message="Product updated successfully",
                data=product
            )

        except Exception as e:
            self.db.rollback()
            raise e

    def delete_product(self, product_id: UUID, business_id: UUID, deleted_by: str):
        try:
            # 1. Find product with all relationships
            product = self.repository.find_by_id_and_business(self.db, product_id, business_id)
            if not product:
                raise NotFoundException(
                    message="Product not found",
                    details={"product_id": str(product_id)}
                )

            # 2. Delete all physical image files
            # Delete main product images
            for image in product.images:
                self._delete_physical_file(image.image_path)
                self.image_repository.soft_delete(self.db, image, deleted_by)

            # 3. Delete variants and their images
            if product.product_type == ProductType.VARIABLE:
                for variant in product.variants:
                    # Delete variant image files
                    for v_image in variant.images:
                        self._delete_physical_file(v_image.image_path)

                    # Soft delete variant
                    self.variant_repository.soft_delete(self.db, variant, deleted_by)

                # Soft delete attributes
                for attribute in product.variant_attributes:
                    self.attribute_repository.soft_delete(self.db, attribute, deleted_by)

            # 4. Soft delete product
            self.repository.soft_delete(self.db, product, deleted_by)

            # 5. Commit
            self.db.commit()

            return SuccessResponse.success(
                message="Product deleted successfully",
                data=None
            )

        except Exception as e:
            self.db.rollback()
            raise e
