from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.modules.order_secret.repository import OrderSecretRepository
from app.modules.order_secret.schema import OrderSecretCreateSchema, OrderSecretUpdateSchema
from app.modules.order_secret.model import OrderSecret
from app.modules.master_type.model import MasterTypes
from app.utils.db_validators import auto_validate
from app.core.response import SuccessResponse
from app.core.exceptions import NotFoundException, ForbiddenException
from app.config.deps import CurrentUser


class OrderSecretUsecase:

    def __init__(self, db: Session):
        self.db = db
        self.repository = OrderSecretRepository()

    def create_order_secret(self, data: OrderSecretCreateSchema, current_user: CurrentUser):
        try:
            if current_user.role != "admin":
                raise ForbiddenException(
                    message="Only admin can create order secrets",
                    details={"required_role": "admin", "current_role": current_user.role}
                )

            marketplace_type = self.db.query(MasterTypes).filter(
                MasterTypes.id == data.marketplace_type_id,
                MasterTypes.deleted_at.is_(None)
            ).first()
            if not marketplace_type:
                raise NotFoundException(
                    message="Marketplace type not found",
                    details={"marketplace_type_id": str(data.marketplace_type_id)}
                )

            auto_validate(
                model=OrderSecret,
                data=data.model_dump(),
                db=self.db
            )

            order_secret_data = {
                "order_secret_id": data.order_secret_id,
                "marketplace_type_id": data.marketplace_type_id,
                "created_by": current_user.email
            }

            order_secret = self.repository.create_order_secret(self.db, order_secret_data)
            self.db.commit()
            self.db.refresh(order_secret)

            return SuccessResponse.created(
                message="Order secret created successfully",
                data=order_secret
            )
        except Exception as e:
            self.db.rollback()
            raise e

    def get_order_secrets(
        self,
        search: Optional[str] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        page: Optional[int] = None,
        per_page: Optional[int] = None
    ):
        from app.utils.query_builder import build_dynamic_query, calculate_pagination_meta

        query = build_dynamic_query(
            db=self.db,
            model=OrderSecret,
            search=search,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            default_sort_field="created_at",
            auto_search_all_fields=True,
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

        if page is not None and per_page is not None:
            count_query = build_dynamic_query(
                db=self.db,
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

    def get_order_secret_by_id(self, order_secret_id: str):
        order_secret = self.repository.find_by_order_secret_id(self.db, order_secret_id)
        if not order_secret:
            raise NotFoundException(
                message="Order secret not found",
                details={"order_secret_id": order_secret_id}
            )

        return SuccessResponse.retrieved(
            message="Order secret retrieved successfully",
            data=order_secret
        )

    def update_order_secret(self, order_secret_id: str, data: OrderSecretUpdateSchema):
        try:
            order_secret = self.repository.find_by_order_secret_id(self.db, order_secret_id)
            if not order_secret:
                raise NotFoundException(
                    message="Order secret not found",
                    details={"order_secret_id": order_secret_id}
                )

            update_data = {
                "message": data.message,
                "emotional": data.emotional,
                "from_name": data.from_name,
                "updated_by": "Customer Update"
            }

            self.repository.update_order_secret(self.db, order_secret, update_data)
            self.db.commit()
            self.db.refresh(order_secret)

            return SuccessResponse.updated(
                message="Order secret updated successfully",
                data=order_secret
            )
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_order_secret(self, order_secret_id: str, current_user: CurrentUser):
        try:
            if current_user.role != "admin":
                raise ForbiddenException(
                    message="Only admin can delete order secrets",
                    details={"required_role": "admin", "current_role": current_user.role}
                )

            order_secret = self.repository.find_by_order_secret_id(self.db, order_secret_id)
            if not order_secret:
                raise NotFoundException(
                    message="Order secret not found",
                    details={"order_secret_id": order_secret_id}
                )

            self.repository.soft_delete(self.db, order_secret, current_user.email)
            self.db.commit()

            return SuccessResponse.deleted(
                message="Order secret deleted successfully"
            )
        except Exception as e:
            self.db.rollback()
            raise e
