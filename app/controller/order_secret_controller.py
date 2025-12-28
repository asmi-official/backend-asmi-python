from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.models.order_secret import OrderSecret
from app.models.master_types import MasterTypes
from app.utils.db_validators import auto_validate
from app.core.exceptions import NotFoundException, ForbiddenException
from app.core.response import SuccessResponse
from app.config.deps import CurrentUser


def create_order_secret(data, db: Session, current_user: CurrentUser):
    try:
        # Validate role - only admin can create
        if current_user.role != "admin":
            raise ForbiddenException(
                message="Only admin can create order secrets",
                details={"required_role": "admin", "current_role": current_user.role}
            )

        # Validate marketplace_type_id exists
        marketplace_type = db.query(MasterTypes).filter(
            MasterTypes.id == data.marketplace_type_id,
            MasterTypes.deleted_at.is_(None)
        ).first()
        if not marketplace_type:
            raise NotFoundException(
                message="Marketplace type not found",
                details={"marketplace_type_id": str(data.marketplace_type_id)}
            )

        # Auto-validate unique fields (order_secret_id) based on model
        auto_validate(
            model=OrderSecret,
            data=data.model_dump(),
            db=db
        )

        order_secret = OrderSecret(
            order_secret_id=data.order_secret_id,
            marketplace_type_id=data.marketplace_type_id,
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
    search: Optional[str] = None,
    filters: Optional[List[Dict[str, Any]]] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
    page: Optional[int] = None,
    per_page: Optional[int] = None
):
    """
    Get list of order secrets with join to master_types

    Args:
        search: Global search based on order_secret_id, created_by, or marketplace type name
        filters: List of filter objects [{key, operator, value}]
                 Supports both OrderSecret fields and MasterTypes fields (e.g., "MasterTypes.name")
        sort_by: Field name for sorting (default: created_at)
                 Supports both OrderSecret fields and MasterTypes fields (e.g., "MasterTypes.name")
        sort_order: "asc" or "desc" (default: desc)
        page: Page number (1-based, optional)
        per_page: Items per page (optional)
    """
    from app.utils.query_builder import build_dynamic_query, calculate_pagination_meta

    # Build query with JOIN support and auto-search all string fields
    query = build_dynamic_query(
        db=db,
        model=OrderSecret,
        search=search,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order,
        default_sort_field="created_at",
        auto_search_all_fields=True,  # Auto-detect all string fields for search
        joins=[
            {
                "model": MasterTypes,
                "condition": OrderSecret.marketplace_type_id == MasterTypes.id,
                "relationship": "marketplace_type",
                "load_only": ["id", "name", "code", "description", "group_code"]
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
                    "model": MasterTypes,
                    "condition": OrderSecret.marketplace_type_id == MasterTypes.id,
                    "relationship": "marketplace_type"
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
    Get order secret by order_secret_id (not UUID id)
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
    Update order secret by order_secret_id (not UUID id)
    """
    try:
        # Find non-deleted order_secret
        order_secret = db.query(OrderSecret).filter(
            OrderSecret.order_secret_id == order_secret_id,
            OrderSecret.deleted_at.is_(None)
        ).first()
        if not order_secret:
            raise NotFoundException(
                message="Order secret not found",
                details={"order_secret_id": order_secret_id}
            )

        # Update fields if provided
        if data.message is not None:
            order_secret.message = data.message
        if data.emotional is not None:
            order_secret.emotional = data.emotional
        if data.from_name is not None:
            order_secret.from_name = data.from_name

        # Set updated_by
        order_secret.updated_by = "Customer Update"  # Customer-initiated update

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
    Soft delete order secret by order_secret_id (not UUID id)
    Admin only
    """
    try:
        # Validate role - only admin can delete
        if current_user.role != "admin":
            raise ForbiddenException(
                message="Only admin can delete order secrets",
                details={"required_role": "admin", "current_role": current_user.role}
            )

        # Find non-deleted order_secret
        order_secret = db.query(OrderSecret).filter(
            OrderSecret.order_secret_id == order_secret_id,
            OrderSecret.deleted_at.is_(None)
        ).first()
        if not order_secret:
            raise NotFoundException(
                message="Order secret not found",
                details={"order_secret_id": order_secret_id}
            )

        # Soft delete - set deleted_at timestamp and deleted_by
        order_secret.deleted_at = datetime.now()
        order_secret.deleted_by = current_user.email

        db.commit()

        return SuccessResponse.deleted(
            message="Order secret deleted successfully"
        )
    except Exception as e:
        db.rollback()
        raise e
