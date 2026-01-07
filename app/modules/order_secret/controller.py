from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.modules.order_secret.usecase import OrderSecretUsecase
from app.modules.order_secret.schema import OrderSecretCreateSchema, OrderSecretUpdateSchema
from app.config.deps import CurrentUser


class OrderSecretController:

    @staticmethod
    def create_order_secret(data: OrderSecretCreateSchema, db: Session, current_user: CurrentUser):
        usecase = OrderSecretUsecase(db)
        return usecase.create_order_secret(data, current_user)

    @staticmethod
    def get_order_secrets(
        db: Session,
        search: Optional[str] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        page: Optional[int] = None,
        per_page: Optional[int] = None
    ):
        usecase = OrderSecretUsecase(db)
        return usecase.get_order_secrets(search, filters, sort_by, sort_order, page, per_page)

    @staticmethod
    def get_order_secret_by_id(order_secret_id: str, db: Session):
        usecase = OrderSecretUsecase(db)
        return usecase.get_order_secret_by_id(order_secret_id)

    @staticmethod
    def update_order_secret(order_secret_id: str, data: OrderSecretUpdateSchema, db: Session):
        usecase = OrderSecretUsecase(db)
        return usecase.update_order_secret(order_secret_id, data)

    @staticmethod
    def delete_order_secret(order_secret_id: str, db: Session, current_user: CurrentUser):
        usecase = OrderSecretUsecase(db)
        return usecase.delete_order_secret(order_secret_id, current_user)
