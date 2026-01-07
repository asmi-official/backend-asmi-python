from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.modules.master_type.usecase import MasterTypeUsecase
from app.modules.master_type.schema import MasterTypesCreateSchema, MasterTypesUpdateSchema


class MasterTypeController:

    @staticmethod
    def create_master_type(data: MasterTypesCreateSchema, db: Session, current_user):
        usecase = MasterTypeUsecase(db)
        return usecase.create_master_type(data, current_user)

    @staticmethod
    def get_master_types(
        db: Session,
        search: Optional[str] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        page: Optional[int] = None,
        per_page: Optional[int] = None
    ):
        usecase = MasterTypeUsecase(db)
        return usecase.get_master_types(search, filters, sort_by, sort_order, page, per_page)

    @staticmethod
    def get_master_type_by_id(master_type_id: str, db: Session):
        usecase = MasterTypeUsecase(db)
        return usecase.get_master_type_by_id(master_type_id)

    @staticmethod
    def update_master_type(master_type_id: str, data: MasterTypesUpdateSchema, db: Session, current_user):
        usecase = MasterTypeUsecase(db)
        return usecase.update_master_type(master_type_id, data, current_user)

    @staticmethod
    def delete_master_type(master_type_id: str, db: Session, current_user):
        usecase = MasterTypeUsecase(db)
        return usecase.delete_master_type(master_type_id, current_user)
