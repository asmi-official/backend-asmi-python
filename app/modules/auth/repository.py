from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, Union
from uuid import UUID
from app.modules.auth.model import User


class AuthRepository:

    @staticmethod
    def create_user(db: Session, user_data: dict) -> User:
        user = User(**user_data)
        db.add(user)
        db.flush()
        return user

    @staticmethod
    def find_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def find_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def find_by_identifier(db: Session, identifier: str) -> Optional[User]:
        return db.query(User).filter(
            or_(
                User.username == identifier,
                User.email == identifier
            )
        ).first()

    @staticmethod
    def find_by_id(db: Session, user_id: Union[str, UUID]) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
