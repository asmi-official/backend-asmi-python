from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.modules.business.repository import BusinessRepository
from app.modules.business.schema import BusinessRegisterSchema, BusinessUpdateSchema
from app.modules.auth.repository import AuthRepository
from app.modules.auth.model import User, UserRole
from app.modules.master_type.model import MasterTypes
from app.modules.naming_series import get_next_code
from app.utils.db_validators import auto_validate
from app.utils.security import hash_password
from app.core.response import SuccessResponse
from app.core.exceptions import NotFoundException


class BusinessUsecase:

    def __init__(self, db: Session):
        self.db = db
        self.repository = BusinessRepository()
        self.auth_repository = AuthRepository()

    def register_business(self, data: BusinessRegisterSchema):
        try:
            # 1. Validate business_type_id exists
            business_type = self.db.query(MasterTypes).filter(
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
                db=self.db,
                validate_required=False
            )

            # 3. Create user with merchant role
            user_data = {
                "name": data.name,
                "email": data.email,
                "username": data.username,
                "password": hash_password(data.password),
                "role": UserRole.merchant
            }
            user = self.auth_repository.create_user(self.db, user_data)

            # 4. Generate business code from naming_series
            business_code = get_next_code(
                code_prefix="BIZ",
                db=self.db,
                padding_length=12,
                description="Business registration code series"
            )

            # 5. Validate business unique fields
            auto_validate(
                model=self.repository.create_business.__self__.__class__,
                data={"business_code": business_code, "email": data.business_email},
                db=self.db,
                validate_required=False
            )

            # 6. Create business
            business_data = {
                "business_code": business_code,
                "business_name": data.business_name,
                "shop_name": data.shop_name,
                "name_owner": data.name,
                "phone": data.phone,
                "email": data.business_email,
                "address": data.address,
                "user_id": user.id,
                "business_type_id": data.business_type_id,
                "status": "trial",
                "created_by": user.email
            }
            business = self.repository.create_business(self.db, business_data)

            # 7. Commit all changes
            self.db.commit()
            self.db.refresh(user)
            self.db.refresh(business)

            return SuccessResponse.created(
                message="Business and user registered successfully",
                data={
                    "user": user,
                    "business": business
                }
            )

        except Exception as e:
            self.db.rollback()
            raise e

    def get_my_businesses(self, user_id: str):
        businesses = self.repository.find_by_user_id(self.db, user_id)
        return SuccessResponse.success(
            message="Businesses retrieved successfully",
            data=businesses
        )

    def get_businesses(
        self,
        search: Optional[str] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        page: Optional[int] = None,
        per_page: Optional[int] = None
    ):
        from app.utils.query_builder import build_dynamic_query, calculate_pagination_meta
        from app.modules.auth.model import User
        from app.modules.business.model import Business

        # Build query with dynamic query builder and JOIN
        query = build_dynamic_query(
            db=self.db,
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
                    "load_only": ["id", "name", "username", "email", "role"]
                },
                {
                    "model": MasterTypes,
                    "condition": Business.business_type_id == MasterTypes.id,
                    "relationship": "business_type",
                    "is_outer": True
                }
            ],
            page=page,
            per_page=per_page
        )

        # Get total count for pagination
        if page is not None and per_page is not None:
            count_query = build_dynamic_query(
                db=self.db,
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

    def get_business_by_id(self, business_id: str, user_id: str):
        business = self.repository.find_by_id_and_user_id(self.db, business_id, user_id)

        if not business:
            raise NotFoundException(
                message="Business not found",
                details={"business_id": business_id}
            )

        return SuccessResponse.success(
            message="Business retrieved successfully",
            data=business
        )

    def update_business(self, business_id: str, data: BusinessUpdateSchema, current_user):
        try:
            # Get business with user relationship
            business = self.repository.find_by_id_and_user_id(
                self.db, business_id, str(current_user.user_id)
            )

            if not business:
                raise NotFoundException(
                    message="Business not found or you don't have access",
                    details={
                        "business_id": business_id,
                        "user_id": str(current_user.user_id)
                    }
                )

            # Get user
            user = self.auth_repository.find_by_id(self.db, business.user_id)
            if not user:
                raise NotFoundException(
                    message="User not found",
                    details={"user_id": str(business.user_id)}
                )

            # Validate business_type_id exists if changed
            if data.business_type_id and data.business_type_id != business.business_type_id:
                business_type = self.db.query(MasterTypes).filter(
                    MasterTypes.id == data.business_type_id,
                    MasterTypes.deleted_at.is_(None)
                ).first()

                if not business_type:
                    raise NotFoundException(
                        message="Business type not found",
                        details={"business_type_id": str(data.business_type_id)}
                    )

            # Validate unique fields
            from app.modules.business.model import Business

            validation_data = {}
            if data.email and data.email != business.email:
                validation_data["email"] = data.email

            if validation_data:
                auto_validate(
                    model=Business,
                    data=validation_data,
                    db=self.db,
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
                    db=self.db,
                    validate_required=False
                )

            # Update user fields
            if data.name:
                user.name = data.name
                business.name_owner = data.name
            if data.username:
                user.username = data.username
            if data.user_email:
                user.email = data.user_email

            # Update business fields
            update_data = {
                "business_name": data.business_name,
                "shop_name": data.shop_name,
                "name_owner": data.name_owner,
                "phone": data.phone,
                "email": data.email,
                "address": data.address,
                "business_type_id": data.business_type_id,
                "status": data.status,
                "updated_by": current_user.email
            }

            self.repository.update_business(self.db, business, update_data)

            self.db.commit()
            self.db.refresh(business)
            self.db.refresh(user)

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
            self.db.rollback()
            raise e
