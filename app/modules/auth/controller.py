from sqlalchemy.orm import Session
from app.modules.auth.usecase import AuthUsecase
from app.modules.auth.schema import RegisterSchema, LoginSchema


class AuthController:

    @staticmethod
    def register(data: RegisterSchema, db: Session):
        usecase = AuthUsecase(db)
        return usecase.register(data)

    @staticmethod
    def login(data: LoginSchema, db: Session):
        usecase = AuthUsecase(db)
        return usecase.login(data)
