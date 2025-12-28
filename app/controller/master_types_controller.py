from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.master_types import MasterTypes
from app.utils.db_validators import auto_validate
from app.core.response import SuccessResponse
from app.core.exceptions import NotFoundException, ForbiddenException


def create_master_type(data, db: Session, current_user):
    """
    Create a new master type with transaction management (Admin only)
    """
    try:
        # Validate role - only admin can create
        if current_user.role != "admin":
            raise ForbiddenException(
                message="Only admin can create master types",
                details={"required_role": "admin", "current_role": current_user.role}
            )

        # Validate unique fields (code)
        auto_validate(
            model=MasterTypes,
            data={"code": data.code},
            db=db,
            validate_required=False
        )

        # Create master type
        master_type = MasterTypes(
            group_code=data.group_code,
            code=data.code,
            name=data.name,
            description=data.description,
            is_active=data.is_active,
            created_by=current_user.email
        )

        db.add(master_type)
        db.commit()
        db.refresh(master_type)

        return SuccessResponse.created(
            message="Master type created successfully",
            data=master_type
        )

    except Exception as e:
        db.rollback()
        raise e


def get_master_types(
    db: Session,
    search: Optional[str] = None,
    filters: Optional[List[Dict[str, Any]]] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
    page: Optional[int] = None,
    per_page: Optional[int] = None
):
    """
    Get all master types with optional filters (Public - No Auth)

    Args:
        search: Global search based on code, name, or description
        filters: List of filter objects [{key, operator, value}]
        sort_by: Field name for sorting (default: group_code)
        sort_order: "asc" or "desc" (default: asc)
        page: Page number (1-based, optional)
        per_page: Items per page (optional)
    """
    from app.utils.query_builder import build_dynamic_query, calculate_pagination_meta

    # Build query with dynamic query builder
    query = build_dynamic_query(
        db=db,
        model=MasterTypes,
        search=search,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order,
        default_sort_field="group_code",
        auto_search_all_fields=True,
        page=page,
        per_page=per_page
    )

    # Get total count for pagination
    if page is not None and per_page is not None:
        count_query = build_dynamic_query(
            db=db,
            model=MasterTypes,
            search=search,
            filters=filters,
            auto_search_all_fields=True
        )
        total = count_query.count()
        pagination_meta = calculate_pagination_meta(total, page, per_page)
    else:
        pagination_meta = None

    master_types = query.all()

    return SuccessResponse.retrieved(
        message="Master types retrieved successfully",
        data=master_types,
        meta=pagination_meta
    )


def get_master_type_by_id(master_type_id: str, db: Session):
    """
    Get detail master type by ID (Public - No Auth)
    """
    try:
        master_type = db.query(MasterTypes).filter(
            MasterTypes.id == master_type_id,
            MasterTypes.deleted_at.is_(None)
        ).first()

        if not master_type:
            raise NotFoundException(
                message="Master type not found",
                details={"master_type_id": master_type_id}
            )

        return SuccessResponse.success(
            message="Master type retrieved successfully",
            data=master_type
        )
    except ValueError:
        # Invalid UUID format
        raise NotFoundException(
            message="Master type not found",
            details={"master_type_id": master_type_id}
        )


def update_master_type(master_type_id: str, data, db: Session, current_user):
    """
    Update master type with transaction management (Admin only)
    """
    try:
        # Validate role - only admin can update
        if current_user.role != "admin":
            raise ForbiddenException(
                message="Only admin can update master types",
                details={"required_role": "admin", "current_role": current_user.role}
            )

        # Get master type
        master_type = db.query(MasterTypes).filter(
            MasterTypes.id == master_type_id,
            MasterTypes.deleted_at.is_(None)
        ).first()

        if not master_type:
            raise NotFoundException(
                message="Master type not found",
                details={"master_type_id": master_type_id}
            )

        # Validate unique fields if code is changed
        if data.code and data.code != master_type.code:
            auto_validate(
                model=MasterTypes,
                data={"code": data.code},
                db=db,
                validate_required=False
            )

        # Update provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(master_type, field, value)

        # Set updated_by
        master_type.updated_by = current_user.email

        db.commit()
        db.refresh(master_type)

        return SuccessResponse.success(
            message="Master type updated successfully",
            data=master_type
        )

    except Exception as e:
        db.rollback()
        raise e


def delete_master_type(master_type_id: str, db: Session, current_user):
    """
    Soft delete master type with transaction management (Admin only)
    """
    try:
        # Validate role - only admin can delete
        if current_user.role != "admin":
            raise ForbiddenException(
                message="Only admin can delete master types",
                details={"required_role": "admin", "current_role": current_user.role}
            )

        # Get master type
        master_type = db.query(MasterTypes).filter(
            MasterTypes.id == master_type_id,
            MasterTypes.deleted_at.is_(None)
        ).first()

        if not master_type:
            raise NotFoundException(
                message="Master type not found",
                details={"master_type_id": master_type_id}
            )

        # Soft delete
        master_type.deleted_at = datetime.now()
        master_type.deleted_by = current_user.email

        db.commit()

        return SuccessResponse.success(
            message="Master type deleted successfully",
            data=None
        )

    except Exception as e:
        db.rollback()
        raise e
