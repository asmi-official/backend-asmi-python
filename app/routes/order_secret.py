from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.deps import get_db, get_current_user, CurrentUser
from app.schemas.order_secret_schema import (
    OrderSecretCreateSchema,
    OrderSecretUpdateSchema
)
from app.controller.order_secret_controller import (
    create_order_secret,
    get_order_secrets,
    get_order_secret_by_id,
    update_order_secret,
    delete_order_secret
)

router = APIRouter()


@router.post("/")
def create(
    data: OrderSecretCreateSchema,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Membuat order secret baru.
    Requires authentication - created_by akan diisi otomatis dari email user yang login.
    """
    return create_order_secret(data, db, current_user)


@router.get("/")
def list_all(
    search: str = None,
    filters: str = None,
    sort_by: str = None,
    sort_order: str = "desc",
    page: int = None,
    per_page: int = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Mengambil semua order secrets dengan filtering, sorting, dan pagination dinamis.

    Query Parameters:
    - search: Global search (order_secret_id, created_by, category name)
    - filters: JSON string array of filter objects
      Format: [{"key": "field_name", "operator": "equal", "value": "value"}]

      Available fields dari OrderSecret:
        - id, order_secret_id, category_marketplace_id, message,
          emotional, from_name, created_at, created_by, updated_at, updated_by

      Available fields dari CategoryMarketplace:
        - name (otomatis detect dari JOIN)
        - description (otomatis detect dari JOIN)
        - Atau gunakan format lengkap: category_marketplace.name, CategoryMarketplace.name

      Operators:
        - equal, not_equal
        - like/contains, starts_with, ends_with
        - gt, gte, lt, lte (untuk tanggal/angka)
        - in, not_in (value harus array)
        - is_null, is_not_null

    - sort_by: Field name untuk sorting (default: created_at)
               Bisa gunakan field dari OrderSecret atau CategoryMarketplace
               (e.g., "category_marketplace.name" atau "CategoryMarketplace.name")
    - sort_order: "asc" atau "desc" (default: desc)
    - page: Page number (1-based, optional)
    - per_page: Items per page (optional)

    Response with pagination:
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

    Examples:
    - ?search=TikTok
    - ?page=1&per_page=10
    - ?filters=[{"key":"order_secret_id","operator":"equal","value":"TBHJG65435O"}]
    - ?filters=[{"key":"emotional","operator":"like","value":"Senang"}]
    - ?filters=[{"key":"name","operator":"equal","value":"TikTok"}]  (otomatis dari CategoryMarketplace)
    - ?filters=[{"key":"category_marketplace.name","operator":"equal","value":"TikTok"}]  (format lengkap)
    - ?sort_by=order_secret_id&sort_order=asc
    - ?sort_by=name&sort_order=asc  (otomatis dari CategoryMarketplace)
    - ?filters=[{"key":"created_at","operator":"gte","value":"2025-12-27"}]&sort_by=created_at&sort_order=desc
    - ?page=2&per_page=20&search=TikTok&sort_by=created_at&sort_order=desc
    """
    import json

    # Parse filters dari JSON string
    parsed_filters = None
    if filters:
        try:
            parsed_filters = json.loads(filters)
        except json.JSONDecodeError:
            parsed_filters = None

    return get_order_secrets(db, search, parsed_filters, sort_by, sort_order, page, per_page)


@router.get("/{order_secret_id}")
def get_by_id(
    order_secret_id: str,
    db: Session = Depends(get_db)
):
    """
    Mengambil detail order secret berdasarkan ID.
    """
    return get_order_secret_by_id(order_secret_id, db)


@router.put("/{order_secret_id}")
def update(
    order_secret_id: str,
    data: OrderSecretUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update order secret.
    """
    return update_order_secret(order_secret_id, data, db)


@router.delete("/{order_secret_id}")
def delete(
    order_secret_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Soft delete order secret.
    Requires authentication - deleted_by akan diisi otomatis dari email user yang login.
    """
    return delete_order_secret(order_secret_id, db, current_user)
