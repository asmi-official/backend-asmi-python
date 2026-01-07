from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID


class OrderSecretCreateSchema(BaseModel):
    order_secret_id: str = Field(
        ...,
        description="ID unik untuk order secret",
        examples=["TBHJG65435O", "ORDER123ABC"]
    )
    marketplace_type_id: UUID = Field(
        ...,
        description="UUID dari MasterTypes marketplace yang sudah ada",
        examples=["2e7e94e4-f711-44e9-b915-0a79aca09e3d"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "order_secret_id": "TBHJG65435O",
                    "marketplace_type_id": "2e7e94e4-f711-44e9-b915-0a79aca09e3d"
                }
            ]
        }
    )


class OrderSecretUpdateSchema(BaseModel):
    message: str | None = Field(
        None,
        description="Pesan dari pengirim",
        examples=["Selamat ulang tahun! Semoga panjang umur dan sehat selalu"]
    )
    emotional: str | None = Field(
        None,
        description="Status emosional pengirim",
        examples=["Senang", "Bahagia", "Haru"]
    )
    from_name: str | None = Field(
        None,
        description="Nama pengirim pesan",
        examples=["Budi", "Siti", "Anonymous"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "message": "Selamat ulang tahun! Semoga panjang umur dan sehat selalu",
                    "emotional": "Senang",
                    "from_name": "Budi"
                }
            ]
        }
    )


class OrderSecretResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_secret_id: str
    marketplace_type_id: UUID
    message: str | None
    emotional: str | None
    from_name: str | None
    created_at: datetime
    created_by: str | None
    updated_at: datetime | None
    updated_by: str | None
    deleted_at: datetime | None
    deleted_by: str | None
