from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class OrderSecretCreateSchema(BaseModel):
    order_secret_id: str
    category_marketplace_id: UUID


class OrderSecretUpdateSchema(BaseModel):
    message: str | None = None
    emotional: str | None = None
    from_name: str | None = None


class OrderSecretResponseSchema(BaseModel):
    id: UUID
    order_secret_id: str
    category_marketplace_id: UUID
    message: str | None
    emotional: str | None
    from_name: str | None
    created_at: datetime
    created_by: str | None
    updated_at: datetime | None
    updated_by: str | None
    deleted_at: datetime | None
    deleted_by: str | None

    class Config:
        from_attributes = True
