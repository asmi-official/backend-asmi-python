from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token
from app.utils.db_validators import auto_validate
from app.config_env import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.exceptions import UnauthorizedException
from app.core.response import SuccessResponse


def register_user(data, db: Session):
    # Auto-validate unique fields (email, username) based on model
    auto_validate(
        model=User,
        data=data.model_dump(),
        db=db,
        validate_required=False  # Pydantic already handles required validation
    )
    user = User(
        name=data.name,
        email=data.email,
        username=data.username,
        password=hash_password(data.password),
        role=data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return SuccessResponse.created(
        message="User registered successfully",
        data=user
    )


def login_user(data, db: Session):
    # Search user by username or email
    user = db.query(User).filter(
        or_(
            User.username == data.identifier,
            User.email == data.identifier
        )
    ).first()

    # User not found
    if not user:
        raise UnauthorizedException(
            message="Invalid credentials",
            details={"reason": "User not found"}
        )

    # Invalid password
    if not verify_password(data.password, user.password):
        raise UnauthorizedException(
            message="Invalid credentials",
            details={"reason": "Invalid password"}
        )

    token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role.value
        },
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    return SuccessResponse.success(
        message="Login successful",
        data={
            "user": user,
            "access_token": token,
            "token_type": "bearer"
        }
    )
