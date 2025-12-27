from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class CategoryMarketplaceCreateSchema(BaseModel):
    name: str
    description: str | None = None


class CategoryMarketplaceUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None


class CategoryMarketplaceResponseSchema(BaseModel):
    id: UUID
    name: str
    description: str | None
    created_at: datetime
    created_by: str | None
    updated_at: datetime | None
    updated_by: str | None
    deleted_at: datetime | None
    deleted_by: str | None

    class Config:
        from_attributes = True 
