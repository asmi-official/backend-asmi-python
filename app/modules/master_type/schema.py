from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from uuid import UUID


class MasterTypesCreateSchema(BaseModel):
    group_code: str = Field(
        ...,
        description="Group code (BUSINESS, PRODUCT, ORDER, USER)",
        examples=["BUSINESS"]
    )
    code: str = Field(
        ...,
        description="Kode unik (max 5 karakter)",
        examples=["ASMI"],
        max_length=5
    )
    name: str = Field(
        ...,
        description="Nama lengkap",
        examples=["Supplier ASMI"]
    )
    description: str | None = Field(
        None,
        description="Deskripsi (optional)",
        examples=["Tipe business untuk supplier ASMI"]
    )
    is_active: bool = Field(
        True,
        description="Status aktif (default: True)"
    )

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str):
        v = v.strip().upper()
        if len(v) > 5:
            raise ValueError("Code maksimal 5 karakter")
        if len(v) < 1:
            raise ValueError("Code minimal 1 karakter")
        return v

    @field_validator("group_code")
    @classmethod
    def validate_group_code(cls, v: str):
        return v.strip().upper()

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "group_code": "BUSINESS",
                    "code": "ASMI",
                    "name": "Supplier ASMI",
                    "description": "Tipe business untuk supplier ASMI",
                    "is_active": True
                }
            ]
        }
    )


class MasterTypesUpdateSchema(BaseModel):
    group_code: str | None = Field(
        None,
        description="Group code (BUSINESS, PRODUCT, ORDER, USER)"
    )
    code: str | None = Field(
        None,
        description="Kode unik (max 5 karakter)",
        max_length=5
    )
    name: str | None = Field(
        None,
        description="Nama lengkap"
    )
    description: str | None = Field(
        None,
        description="Deskripsi"
    )
    is_active: bool | None = Field(
        None,
        description="Status aktif"
    )

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str | None):
        if v is not None:
            v = v.strip().upper()
            if len(v) > 5:
                raise ValueError("Code maksimal 5 karakter")
            if len(v) < 1:
                raise ValueError("Code minimal 1 karakter")
        return v

    @field_validator("group_code")
    @classmethod
    def validate_group_code(cls, v: str | None):
        if v is not None:
            return v.strip().upper()
        return v


class MasterTypesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    group_code: str
    code: str
    name: str
    description: str | None = None
    is_active: bool
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None
