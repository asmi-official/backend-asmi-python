from sqlalchemy.orm import Session
from typing import Optional, List
from app.modules.business.model import Business
from app.modules.auth.model import User


class BusinessRepository:

    @staticmethod
    def create_business(db: Session, business_data: dict) -> Business:
        business = Business(**business_data)
        db.add(business)
        db.flush()
        return business

    @staticmethod
    def find_by_id(db: Session, business_id: str) -> Optional[Business]:
        return db.query(Business).filter(
            Business.id == business_id,
            Business.deleted_at.is_(None)
        ).first()

    @staticmethod
    def find_by_user_id(db: Session, user_id: str) -> List[Business]:
        return db.query(Business).filter(
            Business.user_id == user_id,
            Business.deleted_at.is_(None)
        ).all()

    @staticmethod
    def find_by_id_and_user_id(db: Session, business_id: str, user_id: str) -> Optional[Business]:
        return db.query(Business).filter(
            Business.id == business_id,
            Business.user_id == user_id,
            Business.deleted_at.is_(None)
        ).first()

    @staticmethod
    def find_all(db: Session) -> List[Business]:
        return db.query(Business).filter(
            Business.deleted_at.is_(None)
        ).all()

    @staticmethod
    def update_business(db: Session, business: Business, update_data: dict):
        for key, value in update_data.items():
            if value is not None:
                setattr(business, key, value)
        db.flush()
        return business
