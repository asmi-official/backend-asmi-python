from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from datetime import datetime
from enum import Enum
from uuid import UUID


class RoleEnum(str, Enum):
    admin = "admin"
    karyawan = "karyawan"


class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    username: str
    password: str
    role: RoleEnum

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        v = v.strip()
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password maksimal 72 karakter")
        if len(v) < 6:
            raise ValueError("Password minimal 6 karakter")
        return v


class LoginSchema(BaseModel):
    identifier: str
    password: str


# Response Schemas
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr
    username: str
    role: RoleEnum
    created_at: datetime | None = None
    updated_at: datetime | None = None
