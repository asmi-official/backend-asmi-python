"""
Standard Response Format for all endpoints
Ensures consistent response structure across the application
"""

from typing import Any, Optional
from pydantic import BaseModel
from sqlalchemy.inspection import inspect as sqlalchemy_inspect
from datetime import datetime
from uuid import UUID
from enum import Enum


class SuccessResponse:
    """Helper class to create consistent responses"""

    @staticmethod
    def _serialize_sqlalchemy_model(obj: Any) -> dict:
        """Convert SQLAlchemy model to dict with relationships"""
        result = {}
        mapper = sqlalchemy_inspect(obj)

        # Serialize columns
        for column in mapper.mapper.column_attrs:
            value = getattr(obj, column.key)

            # Skip password field for security
            if column.key == 'password':
                continue

            # Convert special types to JSON-serializable format
            if isinstance(value, UUID):
                result[column.key] = str(value)
            elif isinstance(value, datetime):
                result[column.key] = value.isoformat()
            elif isinstance(value, Enum):
                result[column.key] = value.value
            else:
                result[column.key] = value

        # Serialize relationships (only those already loaded)
        for relationship in mapper.mapper.relationships:
            if relationship.key in mapper.unloaded:
                # Skip relationships that are not yet loaded
                continue

            rel_value = getattr(obj, relationship.key)

            if rel_value is None:
                result[relationship.key] = None
            elif isinstance(rel_value, list):
                # One-to-many or many-to-many relationship
                result[relationship.key] = [
                    SuccessResponse._serialize_sqlalchemy_model(item)
                    for item in rel_value
                ]
            elif hasattr(rel_value, '__table__'):
                # Many-to-one relationship
                result[relationship.key] = SuccessResponse._serialize_sqlalchemy_model(rel_value)
            else:
                result[relationship.key] = rel_value

        return result

    @staticmethod
    def _serialize_data(data: Any) -> Any:
        """Convert Pydantic models or SQLAlchemy models to dict"""
        if isinstance(data, BaseModel):
            return data.model_dump(mode='json')
        elif isinstance(data, list):
            return [SuccessResponse._serialize_data(item) for item in data]
        elif isinstance(data, dict):
            # Recursively serialize dict values
            return {k: SuccessResponse._serialize_data(v) for k, v in data.items()}
        elif hasattr(data, '__table__'):  # SQLAlchemy model
            return SuccessResponse._serialize_sqlalchemy_model(data)
        return data

    @staticmethod
    def success(
        message: str,
        data: Any = None,
        meta: Optional[dict] = None
    ) -> dict:
        """
        Standard format for success response

        Args:
            message: Success message
            data: Returned data (optional) - can be Pydantic model, SQLAlchemy model, or dict
            meta: Additional metadata such as pagination (optional)

        Returns:
            Dictionary with consistent format
        """
        response = {
            "success": True,
            "message": message
        }

        if data is not None:
            response["data"] = SuccessResponse._serialize_data(data)

        if meta is not None:
            response["meta"] = meta

        return response

    @staticmethod
    def created(message: str, data: Any = None) -> dict:
        """Response for successfully created resource (201)"""
        return SuccessResponse.success(message=message, data=data)

    @staticmethod
    def updated(message: str, data: Any = None) -> dict:
        """Response for successfully updated resource"""
        return SuccessResponse.success(message=message, data=data)

    @staticmethod
    def deleted(message: str = "Resource deleted successfully") -> dict:
        """Response for successfully deleted resource"""
        return SuccessResponse.success(message=message)

    @staticmethod
    def retrieved(message: str, data: Any, meta: Optional[dict] = None) -> dict:
        """Response for retrieving data"""
        return SuccessResponse.success(message=message, data=data, meta=meta)
