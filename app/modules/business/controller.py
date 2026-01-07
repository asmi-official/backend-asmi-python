from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.modules.business.usecase import BusinessUsecase
from app.modules.business.schema import BusinessRegisterSchema, BusinessUpdateSchema


class BusinessController:

    @staticmethod
    def register_business(data: BusinessRegisterSchema, db: Session):
        usecase = BusinessUsecase(db)
        return usecase.register_business(data)

    @staticmethod
    def get_my_businesses(user_id: str, db: Session):
        usecase = BusinessUsecase(db)
        return usecase.get_my_businesses(user_id)

    @staticmethod
    def get_businesses(
        db: Session,
        search: Optional[str] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        page: Optional[int] = None,
        per_page: Optional[int] = None
    ):
        usecase = BusinessUsecase(db)
        return usecase.get_businesses(search, filters, sort_by, sort_order, page, per_page)

    @staticmethod
    def get_business_by_id(business_id: str, user_id: str, db: Session):
        usecase = BusinessUsecase(db)
        return usecase.get_business_by_id(business_id, user_id)

    @staticmethod
    def update_business(business_id: str, data: BusinessUpdateSchema, db: Session, current_user):
        usecase = BusinessUsecase(db)
        return usecase.update_business(business_id, data, current_user)
