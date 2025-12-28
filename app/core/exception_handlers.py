"""
Global Exception Handlers
All errors will be handled here and return consistent format
"""

import logging
from datetime import datetime
from typing import Any
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


def create_error_response(
    error_code: str,
    message: str,
    status_code: int,
    path: str,
    details: Any = None
) -> dict:
    """
    Create error response with consistent format

    Format Response:
    {
        "success": false,
        "error": {
            "code": "ERROR_CODE",
            "message": "Error message",
            "details": {...},
            "path": "/api/endpoint",
            "timestamp": "2025-12-20T10:30:45"
        }
    }
    """
    error_response = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "path": path,
            "timestamp": datetime.now().isoformat()
        }
    }

    if details:
        error_response["error"]["details"] = details

    return error_response


async def app_exception_handler(request: Request, exc: AppException):
    """
    Handler for all custom AppException
    """
    logger.error(
        f"AppException: {exc.error_code} - {exc.message} - Path: {request.url.path}",
        exc_info=True
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            error_code=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
            path=request.url.path,
            details=exc.details
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handler for validation errors from Pydantic
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(
        f"Validation Error - Path: {request.url.path} - Errors: {errors}"
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            error_code="VALIDATION_ERROR",
            message="Validation failed",
            status_code=422,
            path=request.url.path,
            details={"errors": errors}
        )
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handler for SQLAlchemy database errors
    """
    logger.error(
        f"Database Error - Path: {request.url.path} - Error: {str(exc)}",
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            error_code="DATABASE_ERROR",
            message="Database error occurred",
            status_code=500,
            path=request.url.path,
            details={"error": str(exc)} if logger.level == logging.DEBUG else None
        )
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handler for all unhandled exceptions
    """
    logger.error(
        f"Unhandled Exception - Path: {request.url.path} - Error: {str(exc)}",
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            status_code=500,
            path=request.url.path,
            details={"error": str(exc)} if logger.level == logging.DEBUG else None
        )
    )


def register_exception_handlers(app):
    """
    Register all exception handlers to FastAPI app
    """
    # Custom app exceptions
    app.add_exception_handler(AppException, app_exception_handler)

    # Validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Database errors
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)

    # Generic errors
    app.add_exception_handler(Exception, generic_exception_handler)
