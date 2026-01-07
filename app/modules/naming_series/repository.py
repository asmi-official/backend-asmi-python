from sqlalchemy.orm import Session
from typing import Optional
from app.modules.naming_series.model import NamingSeries


class NamingSeriesRepository:

    @staticmethod
    def find_by_prefix_with_lock(db: Session, code_prefix: str) -> Optional[NamingSeries]:
        """Get naming series by prefix with row lock for update"""
        return db.query(NamingSeries).filter(
            NamingSeries.code_prefix == code_prefix
        ).with_for_update().first()

    @staticmethod
    def create_naming_series(db: Session, data: dict) -> NamingSeries:
        """Create new naming series"""
        naming_series = NamingSeries(**data)
        db.add(naming_series)
        db.flush()
        return naming_series

    @staticmethod
    def increment_last_number(naming_series: NamingSeries) -> int:
        """Increment and return the next number"""
        naming_series.last_number += 1
        return naming_series.last_number
