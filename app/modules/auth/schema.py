from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime
from enum import Enum
from uuid import UUID


class RoleEnum(str, Enum):
    admin = "admin"
    merchant = "merchant"


class RegisterSchema(BaseModel):
    name: str = Field(
        ...,
        description="Nama lengkap user",
        examples=["John Doe"]
    )
    email: EmailStr = Field(
        ...,
        description="Email user (harus valid dan unique)",
        examples=["john.doe@example.com"]
    )
    username: str = Field(
        ...,
        description="Username (unique)",
        examples=["johndoe"]
    )
    password: str = Field(
        ...,
        description="Password (minimal 6 karakter, maksimal 72 karakter)",
        examples=["password123"]
    )
    role: RoleEnum = Field(
        ...,
        description="Role user: admin atau merchant",
        examples=["merchant"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "username": "johndoe",
                    "password": "password123",
                    "role": "merchant"
                }
            ]
        }
    )

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
    identifier: str = Field(
        ...,
        description="Email atau username untuk login",
        examples=["johndoe"]
    )
    password: str = Field(
        ...,
        description="Password user",
        examples=["password123"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "identifier": "johndoe",
                    "password": "password123"
                }
            ]
        }
    )


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr
    username: str
    role: RoleEnum
    created_at: datetime | None = None
    updated_at: datetime | None = None
