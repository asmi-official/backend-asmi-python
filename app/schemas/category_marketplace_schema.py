"""
Category Marketplace Schemas

Endpoint GET /api/v1/category-marketplaces mendukung fitur-fitur berikut:

1. SEARCH (Global Search)
   - Parameter: search (string, optional)
   - Mencari di semua string fields: name, description, created_by, updated_by
   - Contoh: ?search=tiktok

2. SORTING
   - Parameter: sort_by (string, optional), sort_order (string, optional)
   - sort_by: Field name untuk sorting (default: created_at)
   - sort_order: "asc" atau "desc" (default: desc)

   Contoh:
   - ?sort_by=name&sort_order=asc
   - ?sort_by=created_at&sort_order=desc

3. PAGINATION
   - Parameter: page (integer, optional), per_page (integer, optional)
   - page: Nomor halaman (1-based)
   - per_page: Jumlah item per halaman

   Response dengan pagination:
   {
       "success": true,
       "message": "Category marketplaces retrieved successfully",
       "data": [...],
       "meta": {
           "total": 50,
           "page": 1,
           "per_page": 10,
           "total_pages": 5,
           "has_next": true,
           "has_prev": false
       }
   }

   Contoh:
   - ?page=1&per_page=10
   - ?page=2&per_page=20&search=shopee

4. KOMBINASI
   Semua fitur di atas bisa dikombinasikan:
   - ?search=tiktok&sort_by=name&sort_order=asc&page=1&per_page=10

Note:
- Endpoint ini tidak memiliki filter dinamis seperti order-secrets
- Untuk kebutuhan simple search dan pagination sudah cukup
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID


class CategoryMarketplaceCreateSchema(BaseModel):
    """
    Schema untuk membuat Category Marketplace baru

    Fields:
    - name: Nama marketplace (required, unique)
    - description: Deskripsi marketplace (optional)

    Note:
    - name harus unique untuk records yang tidak dihapus (soft delete support)
    """
    name: str = Field(
        ...,
        description="Nama marketplace (unique)",
        examples=["TikTok", "Shopee", "Tokopedia"]
    )
    description: str | None = Field(
        None,
        description="Deskripsi marketplace",
        examples=["Platform social commerce dengan fitur live streaming", "E-commerce marketplace terpopuler di Asia Tenggara"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "TikTok",
                    "description": "Platform social commerce dengan fitur live streaming"
                }
            ]
        }
    )


class CategoryMarketplaceUpdateSchema(BaseModel):
    """
    Schema untuk update Category Marketplace

    Fields (semua optional):
    - name: Nama marketplace (unique)
    - description: Deskripsi marketplace
    """
    name: str | None = Field(
        None,
        description="Nama marketplace (unique)",
        examples=["TikTok Shop", "Shopee Indonesia"]
    )
    description: str | None = Field(
        None,
        description="Deskripsi marketplace",
        examples=["Platform social commerce dengan fitur live streaming dan shop integration"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "TikTok Shop",
                    "description": "Platform social commerce dengan fitur live streaming dan shop integration"
                }
            ]
        }
    )


class CategoryMarketplaceResponseSchema(BaseModel):
    """
    Schema response Category Marketplace

    Includes all fields dari CategoryMarketplace model
    """
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
