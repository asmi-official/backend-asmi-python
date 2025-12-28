"""
Order Secret Schemas

Endpoint GET /api/v1/order-secrets mendukung fitur-fitur berikut:

1. SEARCH (Global Search)
   - Parameter: search (string, optional)
   - Mencari di semua string fields: order_secret_id, message, emotional, from_name,
     created_by, updated_by, dan fields dari MasterTypes (name, description)
   - Contoh: ?search=TikTok

2. FILTER (Dynamic Filtering)
   - Parameter: filters (JSON string, optional)
   - Format: [{"key": "field_name", "operator": "operator_type", "value": "value"}]

   Available Fields:
   - OrderSecret: order_secret_id, message, emotional, from_name, created_at, created_by, etc.
   - MasterTypes: name, description (gunakan dot notation untuk explisit)

   Available Operators:
   - equal, not_equal
   - like/contains, starts_with, ends_with
   - gt, gte, lt, lte (untuk tanggal/angka)
   - in, not_in (value harus array)
   - is_null, is_not_null

   Contoh:
   - ?filters=[{"key":"emotional","operator":"like","value":"Senang"}]
   - ?filters=[{"key":"name","operator":"equal","value":"TikTok"}]
   - ?filters=[{"key":"marketplace_type.name","operator":"equal","value":"TikTok"}]
   - ?filters=[{"key":"created_at","operator":"gte","value":"2025-12-27"}]

3. SORTING
   - Parameter: sort_by (string, optional), sort_order (string, optional)
   - sort_by: Field name untuk sorting (default: created_at)
   - sort_order: "asc" atau "desc" (default: desc)

   Contoh:
   - ?sort_by=order_secret_id&sort_order=asc
   - ?sort_by=name&sort_order=asc  (dari MasterTypes)
   - ?sort_by=marketplace_type.name&sort_order=desc

4. PAGINATION
   - Parameter: page (integer, optional), per_page (integer, optional)
   - page: Nomor halaman (1-based)
   - per_page: Jumlah item per halaman

   Response dengan pagination:
   {
       "success": true,
       "message": "Order secrets retrieved successfully",
       "data": [...],
       "meta": {
           "total": 100,
           "page": 1,
           "per_page": 10,
           "total_pages": 10,
           "has_next": true,
           "has_prev": false
       }
   }

   Contoh:
   - ?page=1&per_page=10
   - ?page=2&per_page=20&search=TikTok&sort_by=created_at&sort_order=desc

5. KOMBINASI
   Semua fitur di atas bisa dikombinasikan:
   - ?search=Senang&filters=[{"key":"name","operator":"equal","value":"TikTok"}]&sort_by=created_at&sort_order=desc&page=1&per_page=10
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID


class OrderSecretCreateSchema(BaseModel):
    """
    Schema untuk membuat Order Secret baru

    Fields:
    - order_secret_id: ID unik untuk order secret (required)
    - marketplace_type_id: UUID dari MasterTypes marketplace (required)
    """
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
    """
    Schema untuk update Order Secret

    Fields (semua optional):
    - message: Pesan dari pengirim
    - emotional: Status emosional
    - from_name: Nama pengirim
    """
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
    """
    Schema response Order Secret

    Includes all fields dari OrderSecret model
    """
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

    class Config:
        from_attributes = True
