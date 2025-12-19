from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token
from app.utils.db_validators import auto_validate
from app.config_env import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.exceptions import UnauthorizedException


def register_user(data, db: Session):
    # Auto-validate unique fields (email, username) berdasarkan model
    auto_validate(
        model=User,
        data=data.model_dump(),
        db=db,
        validate_required=False  # Pydantic sudah handle required validation
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

    return {"message": "Register success",
            "data": {
                "id":user.id,
                "name":user.name,
                "username":user.username,
                "email":user.email,
                "role": user.role.value

            }}


def login_user(data, db: Session):
    # Cari user berdasarkan username atau email
    user = db.query(User).filter(
        or_(
            User.username == data.identifier,
            User.email == data.identifier
        )
    ).first()

    # User tidak ditemukan
    if not user:
        raise UnauthorizedException(
            message="Invalid credentials",
            details={"reason": "User not found"}
        )

    # Password salah
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

    return {
        "message": "Login success",
        "data": {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "email": user.email,
            "role": user.role.value
        },
        "access_token": token,
        "token_type": "bearer"
    }
