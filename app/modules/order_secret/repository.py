from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.modules.order_secret.model import OrderSecret


class OrderSecretRepository:

    @staticmethod
    def create_order_secret(db: Session, order_secret_data: dict) -> OrderSecret:
        order_secret = OrderSecret(**order_secret_data)
        db.add(order_secret)
        db.flush()
        return order_secret

    @staticmethod
    def find_by_order_secret_id(db: Session, order_secret_id: str) -> Optional[OrderSecret]:
        return db.query(OrderSecret).filter(
            OrderSecret.order_secret_id == order_secret_id,
            OrderSecret.deleted_at.is_(None)
        ).first()

    @staticmethod
    def find_all(db: Session) -> List[OrderSecret]:
        return db.query(OrderSecret).filter(
            OrderSecret.deleted_at.is_(None)
        ).all()

    @staticmethod
    def update_order_secret(db: Session, order_secret: OrderSecret, update_data: dict):
        for key, value in update_data.items():
            if value is not None:
                setattr(order_secret, key, value)
        db.flush()
        return order_secret

    @staticmethod
    def soft_delete(db: Session, order_secret: OrderSecret, deleted_by: str):
        order_secret.deleted_at = datetime.now()
        order_secret.deleted_by = deleted_by
        db.flush()
        return order_secret
