from sqlalchemy.orm import Session
from datetime import datetime

from app.models.order_secret import OrderSecret
from app.models.category_marketplace import CategoryMarketplace
from app.utils.db_validators import auto_validate
from app.core.exceptions import NotFoundException
from app.core.response import SuccessResponse
from app.config.deps import CurrentUser


def create_order_secret(data, db: Session, current_user: CurrentUser):
    try:
        # Validasi category_marketplace_id exists
        category_marketplace = db.query(CategoryMarketplace).filter(
            CategoryMarketplace.id == data.category_marketplace_id,
            CategoryMarketplace.deleted_at.is_(None)
        ).first()
        if not category_marketplace:
            raise NotFoundException(
                message="Category marketplace not found",
                details={"category_marketplace_id": str(data.category_marketplace_id)}
            )

        # Auto-validate unique fields (order_secret_id) berdasarkan model
        auto_validate(
            model=OrderSecret,
            data=data.model_dump(),
            db=db
        )

        order_secret = OrderSecret(
            order_secret_id=data.order_secret_id,
            category_marketplace_id=data.category_marketplace_id,
            created_by=current_user.email
        )

        db.add(order_secret)
        db.commit()
        db.refresh(order_secret)

        return SuccessResponse.created(
            message="Order secret created successfully",
            data=order_secret
        )
    except Exception as e:
        db.rollback()
        raise e


def get_order_secrets(
    db: Session,
    search: str = None,
    filters: list = None,
    sort_by: str = None,
    sort_order: str = "desc",
    page: int = None,
    per_page: int = None
):
    """
    Mendapatkan list order secrets dengan join category_marketplace

    Args:
        search: Global search berdasarkan order_secret_id, created_by, atau category name
        filters: List of filter objects [{key, operator, value}]
                 Supports both OrderSecret fields and CategoryMarketplace fields (e.g., "CategoryMarketplace.name")
        sort_by: Field name untuk sorting (default: created_at)
                 Supports both OrderSecret fields and CategoryMarketplace fields (e.g., "CategoryMarketplace.name")
        sort_order: "asc" atau "desc" (default: desc)
        page: Page number (1-based, optional)
        per_page: Items per page (optional)
    """
    from app.utils.query_builder import build_dynamic_query, calculate_pagination_meta

    # Build query dengan JOIN support dan auto-search semua string fields
    query = build_dynamic_query(
        db=db,
        model=OrderSecret,
        search=search,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order,
        default_sort_field="created_at",
        auto_search_all_fields=True,  # Auto-detect semua string fields untuk search
        joins=[
            {
                "model": CategoryMarketplace,
                "condition": OrderSecret.category_marketplace_id == CategoryMarketplace.id,
                "relationship": "category_marketplace",
                "load_only": ["id", "name", "description"]
            }
        ],
        page=page,
        per_page=per_page
    )

    # Get total count for pagination (before applying limit/offset)
    # We need to build the query again without pagination to get total count
    if page is not None and per_page is not None:
        count_query = build_dynamic_query(
            db=db,
            model=OrderSecret,
            search=search,
            filters=filters,
            auto_search_all_fields=True,
            joins=[
                {
                    "model": CategoryMarketplace,
                    "condition": OrderSecret.category_marketplace_id == CategoryMarketplace.id,
                    "relationship": "category_marketplace"
                }
            ]
        )
        total = count_query.count()
        pagination_meta = calculate_pagination_meta(total, page, per_page)
    else:
        pagination_meta = None

    order_secrets = query.all()

    return SuccessResponse.retrieved(
        message="Order secrets retrieved successfully",
        data=order_secrets,
        meta=pagination_meta
    )


def get_order_secret_by_id(order_secret_id: str, db: Session):
    """
    Mendapatkan order secret berdasarkan order_secret_id (bukan UUID id)
    """
    order_secret = db.query(OrderSecret).filter(
        OrderSecret.order_secret_id == order_secret_id,
        OrderSecret.deleted_at.is_(None)
    ).first()
    if not order_secret:
        raise NotFoundException(
            message="Order secret not found",
            details={"order_secret_id": order_secret_id}
        )

    return SuccessResponse.retrieved(
        message="Order secret retrieved successfully",
        data=order_secret
    )


def update_order_secret(order_secret_id: str, data, db: Session):
    """
    Update order secret berdasarkan order_secret_id (bukan UUID id)
    """
    try:
        # Cari order_secret yang tidak terhapus
        order_secret = db.query(OrderSecret).filter(
            OrderSecret.order_secret_id == order_secret_id,
            OrderSecret.deleted_at.is_(None)
        ).first()
        if not order_secret:
            raise NotFoundException(
                message="Order secret not found",
                details={"order_secret_id": order_secret_id}
            )

        # Update fields jika ada
        if data.message is not None:
            order_secret.message = data.message
        if data.emotional is not None:
            order_secret.emotional = data.emotional
        if data.from_name is not None:
            order_secret.from_name = data.from_name

        # Set updated_by
        order_secret.updated_by = "Customizer Service"  # Placeholder, ganti sesuai kebutuhan

        db.commit()
        db.refresh(order_secret)

        return SuccessResponse.updated(
            message="Order secret updated successfully",
            data=order_secret
        )
    except Exception as e:
        db.rollback()
        raise e


def delete_order_secret(order_secret_id: str, db: Session, current_user: CurrentUser):
    """
    Soft delete order secret berdasarkan order_secret_id (bukan UUID id)
    """
    try:
        # Cari order_secret yang tidak terhapus
        order_secret = db.query(OrderSecret).filter(
            OrderSecret.order_secret_id == order_secret_id,
            OrderSecret.deleted_at.is_(None)
        ).first()
        if not order_secret:
            raise NotFoundException(
                message="Order secret not found",
                details={"order_secret_id": order_secret_id}
            )

        # Soft delete - set deleted_at timestamp dan deleted_by
        order_secret.deleted_at = datetime.now()
        order_secret.deleted_by = current_user.email

        db.commit()

        return SuccessResponse.deleted(
            message="Order secret deleted successfully"
        )
    except Exception as e:
        db.rollback()
        raise e
