from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.auth_schema import RegisterSchema, LoginSchema
from app.controller.auth_controller import register_user, login_user
from app.config.deps import get_db

router = APIRouter()

@router.post("/register")
def register(data: RegisterSchema, db: Session = Depends(get_db)):
    return register_user(data, db)

@router.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):
    return login_user(data, db)
