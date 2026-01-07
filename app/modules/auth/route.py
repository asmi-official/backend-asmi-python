from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.modules.auth.schema import RegisterSchema, LoginSchema
from app.modules.auth.controller import AuthController
from app.config.deps import get_db

router = APIRouter()


@router.post("/register")
def register(data: RegisterSchema, db: Session = Depends(get_db)):
    return AuthController.register(data, db)


@router.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):
    return AuthController.login(data, db)
