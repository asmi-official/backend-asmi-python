from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from enum import Enum
from uuid import UUID


class BusinessStatusEnum(str, Enum):
    trial = "trial"
    active = "active"
    suspended = "suspended"


class BusinessRegisterSchema(BaseModel):
    """
    Schema untuk registrasi business baru (sekaligus create user)
    """
    # User credentials
    name: str = Field(
        ...,
        description="Nama lengkap user/owner",
        examples=["Budi Santoso"]
    )
    username: str = Field(
        ...,
        description="Username untuk login",
        examples=["budisantoso"]
    )
    email: EmailStr = Field(
        ...,
        description="Email user untuk login",
        examples=["budi@example.com"]
    )
    password: str = Field(
        ...,
        description="Password untuk login (minimal 6 karakter)",
        examples=["password123"]
    )

    # Business details
    business_name: str = Field(
        ...,
        description="Nama legal usaha",
        examples=["PT Maju Jaya Abadi"]
    )
    shop_name: str = Field(
        ...,
        description="Nama toko / brand",
        examples=["Toko Maju Jaya"]
    )
    phone: str = Field(
        ...,
        description="Nomor telepon bisnis",
        examples=["081234567890"]
    )
    business_email: EmailStr = Field(
        ...,
        description="Email bisnis",
        examples=["business@majujaya.com"]
    )
    address: str | None = Field(
        None,
        description="Alamat lengkap bisnis",
        examples=["Jl. Raya No. 123, Jakarta"]
    )
    business_type_id: UUID = Field(
        ...,
        description="ID tipe bisnis (required)",
        examples=["2e7e94e4-f711-44e9-b915-0a79aca09e3d"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Budi Santoso",
                    "username": "budisantoso",
                    "email": "budi@example.com",
                    "password": "password123",
                    "business_name": "PT Maju Jaya Abadi",
                    "shop_name": "Toko Maju Jaya",
                    "phone": "081234567890",
                    "business_email": "business@majujaya.com",
                    "address": "Jl. Raya No. 123, Jakarta",
                    "business_type_id": "2e7e94e4-f711-44e9-b915-0a79aca09e3d"
                }
            ]
        }
    )


class BusinessUpdateSchema(BaseModel):
    """
    Schema untuk update business (semua field optional)
    Update username, name, user_email akan update di tabel user juga
    """
    # User fields (akan update di tabel user)
    name: str | None = Field(
        None,
        description="Nama lengkap user/owner (akan update di tabel user)",
        examples=["Budi Santoso"]
    )
    username: str | None = Field(
        None,
        description="Username untuk login (akan update di tabel user)",
        examples=["budisantoso"]
    )
    user_email: EmailStr | None = Field(
        None,
        description="Email user untuk login (akan update di tabel user)",
        examples=["budi@example.com"]
    )

    # Business fields
    business_name: str | None = Field(
        None,
        description="Nama legal usaha",
        examples=["PT Maju Jaya Abadi"]
    )
    shop_name: str | None = Field(
        None,
        description="Nama toko / brand",
        examples=["Toko Maju Jaya"]
    )
    name_owner: str | None = Field(
        None,
        description="Nama pemilik",
        examples=["Budi Santoso"]
    )
    phone: str | None = Field(
        None,
        description="Nomor telepon bisnis",
        examples=["081234567890"]
    )
    email: EmailStr | None = Field(
        None,
        description="Email bisnis",
        examples=["business@majujaya.com"]
    )
    address: str | None = Field(
        None,
        description="Alamat lengkap bisnis",
        examples=["Jl. Raya No. 123, Jakarta"]
    )
    business_type_id: UUID | None = Field(
        None,
        description="ID tipe bisnis"
    )
    status: BusinessStatusEnum | None = Field(
        None,
        description="Status bisnis (trial, active, suspended)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Budi Santoso Updated",
                    "username": "budisantoso_new",
                    "user_email": "budi_new@example.com",
                    "business_name": "PT Maju Jaya Abadi",
                    "shop_name": "Toko Maju Jaya",
                    "phone": "081234567890",
                    "email": "newemail@majujaya.com",
                    "address": "Jl. Baru No. 456, Jakarta"
                }
            ]
        }
    )


class BusinessResponse(BaseModel):
    """
    Schema response untuk business
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_code: str
    business_name: str
    shop_name: str
    name_owner: str
    phone: str
    email: EmailStr
    address: str | None = None
    user_id: UUID
    business_type_id: UUID
    status: BusinessStatusEnum
    created_at: datetime | None = None
    updated_at: datetime | None = None
