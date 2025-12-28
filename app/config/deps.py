from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID

from app.config.database import SessionLocal
from app.config_env import SECRET_KEY, ALGORITHM
from app.core.exceptions import UnauthorizedException
from app.models.user import User

# Security scheme for Swagger UI
security = HTTPBearer(
    scheme_name="Bearer",
    description="Enter your JWT token from /api/v1/auth/login"
)


class CurrentUser(BaseModel):
    """Model for storing current logged-in user information"""
    user_id: UUID
    email: str
    username: str
    role: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> CurrentUser:
    """
    Dependency to retrieve user information from JWT token

    Uses HTTPBearer for integration with Swagger UI.
    Token is automatically extracted from Authorization header: Bearer <token>

    Returns:
        CurrentUser: Object containing user_id, email, username, role

    Raises:
        UnauthorizedException: If token is invalid or user not found
    """
    token = credentials.credentials

    # Decode JWT token
    try:
        if not SECRET_KEY:
            raise UnauthorizedException(
                message="Server configuration error",
                details={"reason": "SECRET_KEY not configured"}
            )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if not user_id:
            raise UnauthorizedException(
                message="Invalid token",
                details={"reason": "Token does not contain user ID"}
            )

    except JWTError as e:
        raise UnauthorizedException(
            message="Could not validate credentials",
            details={"reason": str(e)}
        )

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise UnauthorizedException(
            message="User not found",
            details={"reason": "User from token does not exist"}
        )

    # Return CurrentUser object
    return CurrentUser(
        user_id=user.id,
        email=user.email,
        username=user.username,
        role=user.role.value
    )
