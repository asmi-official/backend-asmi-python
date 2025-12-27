"""
Database Validators
Auto-validate berdasarkan kolom database
"""

from typing import Type, Any, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from app.core.exceptions import ConflictException, ValidationException


def validate_unique_fields(
    model: Type,
    data: Dict[str, Any],
    db: Session,
    exclude_id: Optional[int] = None
) -> None:
    """
    Validasi otomatis untuk unique fields berdasarkan model database

    Args:
        model: SQLAlchemy model class
        data: Dictionary data yang akan divalidasi
        db: Database session
        exclude_id: ID untuk di-exclude (untuk update)

    Raises:
        ConflictException: Jika ada field yang sudah exist di database

    Example:
        validate_unique_fields(User, {"email": "test@test.com"}, db)
    """
    # Get model inspector
    mapper = inspect(model)

    # Loop semua columns di model
    for column in mapper.columns:
        # Check jika column unique
        if column.unique and column.name in data:
            value = data[column.name]

            # Skip jika value None atau empty
            if not value:
                continue

            # Query untuk check apakah value sudah ada
            query = db.query(model).filter(
                getattr(model, column.name) == value
            )

            # Exclude soft deleted records (jika model punya deleted_at)
            if hasattr(model, 'deleted_at'):
                query = query.filter(model.deleted_at.is_(None))

            # Exclude ID tertentu (untuk update)
            if exclude_id:
                query = query.filter(model.id != exclude_id)

            existing = query.first()

            # Jika sudah ada, raise conflict
            if existing:
                raise ConflictException(
                    message=f"{column.name.capitalize()} already exists",
                    details={
                        "field": column.name,
                        "value": value,
                        "constraint": "unique"
                    }
                )


def validate_required_fields(
    model: Type,
    data: Dict[str, Any],
    exclude_fields: list = None
) -> None:
    """
    Validasi otomatis untuk required fields (nullable=False)

    Args:
        model: SQLAlchemy model class
        data: Dictionary data yang akan divalidasi
        exclude_fields: List field yang di-exclude dari validasi

    Raises:
        ValidationException: Jika ada required field yang missing

    Example:
        validate_required_fields(User, {"name": "John"}, exclude_fields=["id", "created_at"])
    """
    exclude_fields = exclude_fields or ["id", "created_at", "updated_at"]
    mapper = inspect(model)

    missing_fields = []

    for column in mapper.columns:
        # Skip excluded fields
        if column.name in exclude_fields:
            continue

        # Check jika column required (not nullable) dan tidak ada di data
        if not column.nullable and column.name not in data:
            missing_fields.append(column.name)

    if missing_fields:
        raise ValidationException(
            message="Required fields are missing",
            details={
                "missing_fields": missing_fields
            }
        )


def validate_field_length(
    model: Type,
    data: Dict[str, Any]
) -> None:
    """
    Validasi otomatis untuk max length berdasarkan column length

    Args:
        model: SQLAlchemy model class
        data: Dictionary data yang akan divalidasi

    Raises:
        ValidationException: Jika ada field yang melebihi max length

    Example:
        validate_field_length(User, {"name": "Very long name..."})
    """
    mapper = inspect(model)
    validation_errors = []

    for column in mapper.columns:
        if column.name not in data:
            continue

        value = data[column.name]

        # Skip jika value bukan string
        if not isinstance(value, str):
            continue

        # Check max length jika column punya length
        if hasattr(column.type, 'length') and column.type.length:
            max_length = column.type.length

            if len(value) > max_length:
                validation_errors.append({
                    "field": column.name,
                    "value_length": len(value),
                    "max_length": max_length,
                    "message": f"{column.name} must be at most {max_length} characters"
                })

    if validation_errors:
        raise ValidationException(
            message="Field length validation failed",
            details={"errors": validation_errors}
        )


def auto_validate(
    model: Type,
    data: Dict[str, Any],
    db: Session,
    exclude_id: Optional[int] = None,
    validate_required: bool = False,
    exclude_required_fields: list = None
) -> None:
    """
    Validasi otomatis lengkap (unique, required, length)

    Args:
        model: SQLAlchemy model class
        data: Dictionary data yang akan divalidasi
        db: Database session
        exclude_id: ID untuk di-exclude (untuk update)
        validate_required: Apakah validate required fields
        exclude_required_fields: List field yang di-exclude dari validasi required

    Example:
        # Untuk create
        auto_validate(User, {"email": "test@test.com"}, db, validate_required=True)

        # Untuk update
        auto_validate(User, {"email": "newemail@test.com"}, db, exclude_id=1)
    """
    # Validate unique fields
    validate_unique_fields(model, data, db, exclude_id)

    # Validate field length
    validate_field_length(model, data)

    # Validate required fields (optional)
    if validate_required:
        validate_required_fields(model, data, exclude_required_fields)
