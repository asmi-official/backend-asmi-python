"""
Custom Exception Classes untuk aplikasi
Semua error response akan mengikuti format yang sama
"""

from typing import Any, Optional


class AppException(Exception):
    """Base exception untuk semua custom exceptions"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details
        super().__init__(self.message)


# ===============================
# Authentication & Authorization Errors (401, 403)
# ===============================

class UnauthorizedException(AppException):
    """401 - User tidak ter-autentikasi"""

    def __init__(self, message: str = "Unauthorized", details: Any = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED",
            details=details
        )


class ForbiddenException(AppException):
    """403 - User tidak punya akses"""

    def __init__(self, message: str = "Forbidden", details: Any = None):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
            details=details
        )


# ===============================
# Resource Errors (404, 409)
# ===============================

class NotFoundException(AppException):
    """404 - Resource tidak ditemukan"""

    def __init__(self, message: str = "Resource not found", details: Any = None):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details=details
        )


class ConflictException(AppException):
    """409 - Konflik data (misal: email sudah ada)"""

    def __init__(self, message: str = "Conflict", details: Any = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details=details
        )


# ===============================
# Validation Errors (422)
# ===============================

class ValidationException(AppException):
    """422 - Validasi data gagal"""

    def __init__(self, message: str = "Validation failed", details: Any = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details
        )


# ===============================
# Server Errors (500, 503)
# ===============================

class InternalServerException(AppException):
    """500 - Internal server error"""

    def __init__(self, message: str = "Internal server error", details: Any = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="INTERNAL_SERVER_ERROR",
            details=details
        )


class ServiceUnavailableException(AppException):
    """503 - Service tidak tersedia"""

    def __init__(self, message: str = "Service unavailable", details: Any = None):
        super().__init__(
            message=message,
            status_code=503,
            error_code="SERVICE_UNAVAILABLE",
            details=details
        )


# ===============================
# Business Logic Errors (400)
# ===============================

class BadRequestException(AppException):
    """400 - Bad request"""

    def __init__(self, message: str = "Bad request", details: Any = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="BAD_REQUEST",
            details=details
        )


# ===============================
# Database Errors
# ===============================

class DatabaseException(AppException):
    """Database error"""

    def __init__(self, message: str = "Database error", details: Any = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details=details
        )
