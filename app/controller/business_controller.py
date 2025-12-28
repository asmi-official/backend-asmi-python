from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.models.user import User, UserRole
from app.models.business import Business, BusinessStatus
from app.models.master_types import MasterTypes
from app.utils.db_validators import auto_validate
from app.utils.naming_series import get_next_code
from app.utils.security import hash_password
from app.core.response import SuccessResponse
from app.core.exceptions import NotFoundException


def register_business(data, db: Session):
    """
    Register a new business (and simultaneously create a user)

    Args:
        data: BusinessRegisterSchema (includes user credentials and business details)
        db: Database session
    """
    try:
        # 1. Validate business_type_id exists
        business_type = db.query(MasterTypes).filter(
            MasterTypes.id == data.business_type_id,
            MasterTypes.deleted_at.is_(None)
        ).first()

        if not business_type:
            raise NotFoundException(
                message="Business type not found",
                details={"business_type_id": str(data.business_type_id)}
            )

        # 2. Validate user unique fields (email, username)
        auto_validate(
            model=User,
            data={"email": data.email, "username": data.username},
            db=db,
            validate_required=False
        )

        # 3. Create user with merchant role
        user = User(
            name=data.name,
            email=data.email,
            username=data.username,
            password=hash_password(data.password),
            role=UserRole.merchant  # Default role for business registration
        )
        db.add(user)
        db.flush()  # Flush to obtain user.id

        # 4. Generate business code from naming_series
        business_code = get_next_code(
            code_prefix="BIZ",
            db=db,
            padding_length=12,
            description="Business registration code series"
        )

        # 5. Validate business unique fields
        auto_validate(
            model=Business,
            data={"business_code": business_code, "email": data.business_email},
            db=db,
            validate_required=False
        )

        # 6. Create business
        business = Business(
            business_code=business_code,
            business_name=data.business_name,
            shop_name=data.shop_name,
            name_owner=data.name,  # Use user name as owner
            phone=data.phone,
            email=data.business_email,
            address=data.address,
            user_id=user.id,  # Link to the newly created user
            business_type_id=data.business_type_id,
            status=BusinessStatus.trial,  # Default status is trial
            created_by=user.email  # Email of the user creating this
        )
        db.add(business)

        # 7. Commit all changes (user + naming_series + business)
        db.commit()
        db.refresh(user)
        db.refresh(business)

        return SuccessResponse.created(
            message="Business and user registered successfully",
            data={
                "user": user,
                "business": business
            }
        )

    except Exception as e:
        # Rollback all changes if there is an error
        # Including user, naming_series, and business
        db.rollback()
        raise e


def get_my_businesses(user_id: str, db: Session):
    """
    Get all businesses owned by the currently logged-in user
    """
    businesses = db.query(Business).filter(
        Business.user_id == user_id,
        Business.deleted_at.is_(None)
    ).all()

    return SuccessResponse.success(
        message="Businesses retrieved successfully",
        data=businesses
    )


def get_businesses(
    db: Session,
    search: Optional[str] = None,
    filters: Optional[List[Dict[str, Any]]] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
    page: Optional[int] = None,
    per_page: Optional[int] = None
):
    """
    Get all businesses with filters and pagination (Admin only)
    Includes JOIN with user and master_types

    Args:
        search: Global search based on business_code, business_name, shop_name, email
        filters: List of filter objects [{key, operator, value}]
        sort_by: Field name for sorting (default: created_at)
        sort_order: "asc" or "desc" (default: desc)
        page: Page number (1-based, optional)
        per_page: Items per page (optional)
    """
    from app.utils.query_builder import build_dynamic_query, calculate_pagination_meta
    from app.models.master_types import MasterTypes

    # Build query with dynamic query builder and JOIN
    query = build_dynamic_query(
        db=db,
        model=Business,
        search=search,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order,
        default_sort_field="created_at",
        auto_search_all_fields=True,
        joins=[
            {
                "model": User,
                "condition": Business.user_id == User.id,
                "relationship": "user",
                "load_only": ["id", "name", "username", "email", "role"]  # Exclude password
            },
            {
                "model": MasterTypes,
                "condition": Business.business_type_id == MasterTypes.id,
                "relationship": "business_type",
                "is_outer": True  # LEFT JOIN because business_type_id is nullable
            }
        ],
        page=page,
        per_page=per_page
    )

    # Get total count for pagination
    if page is not None and per_page is not None:
        count_query = build_dynamic_query(
            db=db,
            model=Business,
            search=search,
            filters=filters,
            auto_search_all_fields=True,
            joins=[
                {
                    "model": User,
                    "condition": Business.user_id == User.id,
                    "relationship": "user"
                },
                {
                    "model": MasterTypes,
                    "condition": Business.business_type_id == MasterTypes.id,
                    "relationship": "business_type",
                    "is_outer": True
                }
            ]
        )
        total = count_query.count()
        pagination_meta = calculate_pagination_meta(total, page, per_page)
    else:
        pagination_meta = None

    businesses = query.all()

    return SuccessResponse.retrieved(
        message="Businesses retrieved successfully",
        data=businesses,
        meta=pagination_meta
    )


def get_business_by_id(business_id: str, user_id: str, db: Session):
    """
    Get business details by ID
    Can only be accessed by the business owner
    """
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == user_id,
        Business.deleted_at.is_(None)
    ).first()

    if not business:
        raise NotFoundException(
            message="Business not found",
            details={"business_id": business_id}
        )

    return SuccessResponse.success(
        message="Business retrieved successfully",
        data=business
    )


def update_business(business_id: str, data, db: Session, current_user):
    """
    Update business and user with transaction management
    """
    try:
        # Get business with user relationship
        business = db.query(Business).filter(
            Business.id == business_id,
            Business.user_id == current_user.user_id,
            Business.deleted_at.is_(None)
        ).first()

        if not business:
            raise NotFoundException(
                message="Business not found or you don't have access",
                details={
                    "business_id": business_id,
                    "user_id": str(current_user.user_id),
                    "deleted_at": "IS NULL (only active businesses)"
                }
            )

        # Get user
        user = db.query(User).filter(User.id == business.user_id).first()
        if not user:
            raise NotFoundException(
                message="User not found",
                details={
                    "user_id": str(business.user_id),
                    "deleted_at": "IS NULL (only active businesses)"
               }
            )

        # Validate business_type_id exists if changed
        if data.business_type_id and data.business_type_id != business.business_type_id:
            business_type = db.query(MasterTypes).filter(
                MasterTypes.id == data.business_type_id,
                MasterTypes.deleted_at.is_(None)
            ).first()

            if not business_type:
                raise NotFoundException(
                    message="Business type not found",
                    details={"business_type_id": str(data.business_type_id)}
                )

        # Validate unique fields
        validation_data = {}

        # Validate business email if changed
        if data.email and data.email != business.email:
            validation_data["email"] = data.email

        if validation_data:
            auto_validate(
                model=Business,
                data=validation_data,
                db=db,
                validate_required=False
            )

        # Validate user fields if changed
        user_validation_data = {}
        if data.username and data.username != user.username:
            user_validation_data["username"] = data.username
        if data.user_email and data.user_email != user.email:
            user_validation_data["email"] = data.user_email

        if user_validation_data:
            auto_validate(
                model=User,
                data=user_validation_data,
                db=db,
                validate_required=False
            )

        # Update user fields
        if data.name:
            user.name = data.name
            business.name_owner = data.name  # Also update name_owner
        if data.username:
            user.username = data.username
        if data.user_email:
            user.email = data.user_email

        # Update business fields - update all provided fields
        if data.business_name:
            business.business_name = data.business_name
        if data.shop_name:
            business.shop_name = data.shop_name
        if data.name_owner:
            business.name_owner = data.name_owner
        if data.phone:
            business.phone = data.phone
        if data.email:
            business.email = data.email
        if data.address:
            business.address = data.address
        if data.business_type_id:
            business.business_type_id = data.business_type_id
        if data.status:
            business.status = data.status

        # Set updated_by
        business.updated_by = current_user.email

        db.commit()
        db.refresh(business)
        db.refresh(user)

        return SuccessResponse.success(
            message="Business and user updated successfully",
            data={
                "business": business,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role
                }
            }
        )

    except Exception as e:
        db.rollback()
        raise e
