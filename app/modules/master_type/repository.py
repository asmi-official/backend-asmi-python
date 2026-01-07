from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.modules.master_type.model import MasterTypes


class MasterTypeRepository:

    @staticmethod
    def create_master_type(db: Session, master_type_data: dict) -> MasterTypes:
        master_type = MasterTypes(**master_type_data)
        db.add(master_type)
        db.flush()
        return master_type

    @staticmethod
    def find_by_id(db: Session, master_type_id: str) -> Optional[MasterTypes]:
        return db.query(MasterTypes).filter(
            MasterTypes.id == master_type_id,
            MasterTypes.deleted_at.is_(None)
        ).first()

    @staticmethod
    def find_by_code(db: Session, code: str) -> Optional[MasterTypes]:
        return db.query(MasterTypes).filter(
            MasterTypes.code == code,
            MasterTypes.deleted_at.is_(None)
        ).first()

    @staticmethod
    def find_all(db: Session) -> List[MasterTypes]:
        return db.query(MasterTypes).filter(
            MasterTypes.deleted_at.is_(None)
        ).all()

    @staticmethod
    def update_master_type(db: Session, master_type: MasterTypes, update_data: dict):
        for key, value in update_data.items():
            if value is not None:
                setattr(master_type, key, value)
        db.flush()
        return master_type

    @staticmethod
    def soft_delete(db: Session, master_type: MasterTypes, deleted_by: str):
        master_type.deleted_at = datetime.now()
        master_type.deleted_by = deleted_by
        db.flush()
        return master_type
