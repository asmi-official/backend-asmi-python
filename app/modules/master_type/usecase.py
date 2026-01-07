from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.modules.master_type.repository import MasterTypeRepository
from app.modules.master_type.schema import MasterTypesCreateSchema, MasterTypesUpdateSchema
from app.modules.master_type.model import MasterTypes
from app.utils.db_validators import auto_validate
from app.core.response import SuccessResponse
from app.core.exceptions import NotFoundException, ForbiddenException


class MasterTypeUsecase:

    def __init__(self, db: Session):
        self.db = db
        self.repository = MasterTypeRepository()

    def create_master_type(self, data: MasterTypesCreateSchema, current_user):
        try:
            if current_user.role != "admin":
                raise ForbiddenException(
                    message="Only admin can create master types",
                    details={"required_role": "admin", "current_role": current_user.role}
                )

            auto_validate(
                model=MasterTypes,
                data={"code": data.code},
                db=self.db,
                validate_required=False
            )

            master_type_data = {
                "group_code": data.group_code,
                "code": data.code,
                "name": data.name,
                "description": data.description,
                "is_active": data.is_active,
                "created_by": current_user.email
            }

            master_type = self.repository.create_master_type(self.db, master_type_data)
            self.db.commit()
            self.db.refresh(master_type)

            return SuccessResponse.created(
                message="Master type created successfully",
                data=master_type
            )

        except Exception as e:
            self.db.rollback()
            raise e

    def get_master_types(
        self,
        search: Optional[str] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        page: Optional[int] = None,
        per_page: Optional[int] = None
    ):
        from app.utils.query_builder import build_dynamic_query, calculate_pagination_meta

        query = build_dynamic_query(
            db=self.db,
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

        if page is not None and per_page is not None:
            count_query = build_dynamic_query(
                db=self.db,
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

    def get_master_type_by_id(self, master_type_id: str):
        try:
            master_type = self.repository.find_by_id(self.db, master_type_id)

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
            raise NotFoundException(
                message="Master type not found",
                details={"master_type_id": master_type_id}
            )

    def update_master_type(self, master_type_id: str, data: MasterTypesUpdateSchema, current_user):
        try:
            if current_user.role != "admin":
                raise ForbiddenException(
                    message="Only admin can update master types",
                    details={"required_role": "admin", "current_role": current_user.role}
                )

            master_type = self.repository.find_by_id(self.db, master_type_id)

            if not master_type:
                raise NotFoundException(
                    message="Master type not found",
                    details={"master_type_id": master_type_id}
                )

            if data.code and data.code != master_type.code:
                auto_validate(
                    model=MasterTypes,
                    data={"code": data.code},
                    db=self.db,
                    validate_required=False
                )

            update_data = data.model_dump(exclude_unset=True)
            update_data["updated_by"] = current_user.email

            self.repository.update_master_type(self.db, master_type, update_data)
            self.db.commit()
            self.db.refresh(master_type)

            return SuccessResponse.success(
                message="Master type updated successfully",
                data=master_type
            )

        except Exception as e:
            self.db.rollback()
            raise e

    def delete_master_type(self, master_type_id: str, current_user):
        try:
            if current_user.role != "admin":
                raise ForbiddenException(
                    message="Only admin can delete master types",
                    details={"required_role": "admin", "current_role": current_user.role}
                )

            master_type = self.repository.find_by_id(self.db, master_type_id)

            if not master_type:
                raise NotFoundException(
                    message="Master type not found",
                    details={"master_type_id": master_type_id}
                )

            self.repository.soft_delete(self.db, master_type, current_user.email)
            self.db.commit()

            return SuccessResponse.success(
                message="Master type deleted successfully",
                data=None
            )

        except Exception as e:
            self.db.rollback()
            raise e
