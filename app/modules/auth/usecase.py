from sqlalchemy.orm import Session
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schema import RegisterSchema, LoginSchema
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token
from app.utils.db_validators import auto_validate
from app.config_env import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.exceptions import UnauthorizedException
from app.core.response import SuccessResponse
from app.modules.auth.model import User


class AuthUsecase:

    def __init__(self, db: Session):
        self.db = db
        self.repository = AuthRepository()

    def register(self, data: RegisterSchema):
        auto_validate(
            model=User,
            data=data.model_dump(),
            db=self.db,
            validate_required=False
        )

        user_data = {
            "name": data.name,
            "email": data.email,
            "username": data.username,
            "password": hash_password(data.password),
            "role": data.role
        }

        user = self.repository.create_user(self.db, user_data)
        self.db.commit()
        self.db.refresh(user)

        return SuccessResponse.created(
            message="User registered successfully",
            data=user
        )

    def login(self, data: LoginSchema):
        user = self.repository.find_by_identifier(self.db, data.identifier)

        if not user:
            raise UnauthorizedException(
                message="Invalid credentials",
                details={"reason": "User not found"}
            )

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
