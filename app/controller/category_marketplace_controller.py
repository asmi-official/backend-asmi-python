from sqlalchemy.orm import Session

from app.models.category_marketplace import CategoryMarketplace
from app.utils.db_validators import auto_validate
from app.core.exceptions import NotFoundException
from app.core.response import SuccessResponse
from app.config.deps import CurrentUser


def create_category_marketplace(data, db: Session, current_user: CurrentUser):
    try:
        # Auto-validate unique fields (name) berdasarkan model
        auto_validate(
            model=CategoryMarketplace,
            data=data.model_dump(),
            db=db
        )

        category_marketplace = CategoryMarketplace(
            name=data.name,
            description=data.description,
            created_by=current_user.email
        )

        db.add(category_marketplace)
        db.commit()
        db.refresh(category_marketplace)

        return SuccessResponse.created(
            message="Category marketplace created successfully",
            data=category_marketplace
        )
    except Exception as e:
        db.rollback()
        raise e


def get_category_marketplaces(
    db: Session,
    search: str = None,
    page: int = None,
    per_page: int = None
):
    """
    Mendapatkan list category marketplaces dengan optional search dan pagination

    Args:
        search: Search string untuk mencari berdasarkan name atau description
        page: Page number (1-based, optional)
        per_page: Items per page (optional)
    """
    from app.utils.query_builder import build_dynamic_query, calculate_pagination_meta

    # Build query dengan auto-search semua string fields
    query = build_dynamic_query(
        db=db,
        model=CategoryMarketplace,
        search=search,
        auto_search_all_fields=True,  # Auto-detect semua string fields (name, description, dll)
        sort_by="created_at",
        sort_order="desc",
        page=page,
        per_page=per_page
    )

    # Get total count for pagination (before applying limit/offset)
    if page is not None and per_page is not None:
        count_query = build_dynamic_query(
            db=db,
            model=CategoryMarketplace,
            search=search,
            auto_search_all_fields=True
        )
        total = count_query.count()
        pagination_meta = calculate_pagination_meta(total, page, per_page)
    else:
        pagination_meta = None

    categories = query.all()

    return SuccessResponse.retrieved(
        message="Category marketplaces retrieved successfully",
        data=categories,
        meta=pagination_meta
    )


def get_category_marketplace_by_id(category_marketplace_id: str, db: Session):
    """
    Mendapatkan detail category marketplace berdasarkan ID
    """
    category_marketplace = db.query(CategoryMarketplace).filter(
        CategoryMarketplace.id == category_marketplace_id,
        CategoryMarketplace.deleted_at.is_(None)
    ).first()

    if not category_marketplace:
        raise NotFoundException(
            message="Category marketplace not found",
            details={"category_marketplace_id": category_marketplace_id}
        )

    return SuccessResponse.retrieved(
        message="Category marketplace retrieved successfully",
        data=category_marketplace
    )


def update_category_marketplace(category_marketplace_id: str, data, db: Session, current_user: CurrentUser):
    try:
        # Cari category marketplace yang tidak terhapus
        category_marketplace = db.query(CategoryMarketplace).filter(
            CategoryMarketplace.id == category_marketplace_id,
            CategoryMarketplace.deleted_at.is_(None)
        ).first()
        if not category_marketplace:
            raise NotFoundException(
                message="Category marketplace not found",
                details={"category_marketplace_id": category_marketplace_id}
            )

        # Auto-validate unique fields, exclude current category ID
        auto_validate(
            model=CategoryMarketplace,
            data=data.model_dump(exclude_unset=True),
            db=db,
            exclude_id=category_marketplace_id
        )

        # Update fields jika ada
        if data.name is not None:
            category_marketplace.name = data.name
        if data.description is not None:
            category_marketplace.description = data.description

        # Set updated_by
        category_marketplace.updated_by = current_user.email

        db.commit()
        db.refresh(category_marketplace)

        return SuccessResponse.updated(
            message="Category marketplace updated successfully",
            data=category_marketplace
        )
    except Exception as e:
        db.rollback()
        raise e


def delete_category_marketplace(category_marketplace_id: str, db: Session, current_user: CurrentUser):
    try:
        # Cari category marketplace yang tidak terhapus
        category_marketplace = db.query(CategoryMarketplace).filter(
            CategoryMarketplace.id == category_marketplace_id,
            CategoryMarketplace.deleted_at.is_(None)
        ).first()
        if not category_marketplace:
            raise NotFoundException(
                message="Category marketplace not found",
                details={"category_marketplace_id": category_marketplace_id}
            )

        # Soft delete - set deleted_at timestamp dan deleted_by
        from datetime import datetime
        category_marketplace.deleted_at = datetime.now()
        category_marketplace.deleted_by = current_user.email

        db.commit()

        return SuccessResponse.deleted(
            message="Category marketplace deleted successfully"
        )
    except Exception as e:
        db.rollback()
        raise e
