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

# Security scheme untuk Swagger UI
security = HTTPBearer(
    scheme_name="Bearer",
    description="Enter your JWT token from /api/v1/auth/login"
)


class CurrentUser(BaseModel):
    """Model untuk menyimpan informasi user yang sedang login"""
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
    Dependency untuk mendapatkan informasi user dari JWT token

    Menggunakan HTTPBearer untuk integrasi dengan Swagger UI.
    Token akan otomatis diambil dari header Authorization: Bearer <token>

    Returns:
        CurrentUser: Object berisi user_id, email, username, role

    Raises:
        UnauthorizedException: Jika token invalid atau user tidak ditemukan
    """
    token = credentials.credentials

    # Decode JWT token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise UnauthorizedException(
                message="Invalid token",
                details={"reason": "Token does not contain user ID"}
            )

    except JWTError as e:
        raise UnauthorizedException(
            message="Could not validate credentials",
            details={"reason": str(e)}
        )

    # Get user dari database
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
