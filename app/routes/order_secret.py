from fastapi import APIRouter, Depends, Query
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


@router.post("/", summary="Create order secret")
def create(
    data: OrderSecretCreateSchema,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Membuat order secret baru berdasarkan order ID dari marketplace.

    **Authentication required**: Bearer token dari login

    **Request Body**:
    - `order_secret_id`: ID unik order dari marketplace (required, unique)
    - `category_marketplace_id`: UUID category marketplace yang sudah ada (required)

    **Validations**:
    - `order_secret_id` harus unique
    - `category_marketplace_id` harus exist dan tidak terhapus

    **Auto-filled**:
    - `created_by`: Email dari user yang login
    - `created_at`: Timestamp otomatis
    - Fields lain (message, emotional, from_name) akan null sampai di-update

    **Flow**:
    1. Sistem menerima order_secret_id dari marketplace
    2. Create record dengan status kosong
    3. Customer nanti mengisi message, emotional, from_name via update endpoint
    """
    return create_order_secret(data, db, current_user)


@router.get("/")
def list_all(
    search: str = Query(
        None,
        description="Global search di semua string fields (order_secret_id, message, emotional, from_name, created_by, updated_by, category name, category description)",
        example="TikTok"
    ),
    filters: str = Query(
        None,
        description='Dynamic filtering - JSON array format: [{"key": "field_name", "operator": "operator_type", "value": "value"}]. Operators: equal, not_equal, like, contains, starts_with, ends_with, gt, gte, lt, lte, in, not_in, is_null, is_not_null',
        example='[{"key":"emotional","operator":"like","value":"Senang"}]'
    ),
    sort_by: str = Query(
        None,
        description="Field name untuk sorting (support main table dan joined table dengan dot notation). Default: created_at",
        example="created_at"
    ),
    sort_order: str = Query(
        "desc",
        description="Sort order: asc atau desc",
        example="desc"
    ),
    page: int = Query(
        None,
        description="Page number (1-based). Harus dikombinasikan dengan per_page untuk mendapat pagination meta",
        example=1,
        ge=1
    ),
    per_page: int = Query(
        None,
        description="Items per page. Harus dikombinasikan dengan page untuk mendapat pagination meta",
        example=10,
        ge=1,
        le=100
    ),
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


@router.get("/{order_secret_id}", summary="Get order secret by ID")
def get_by_id(
    order_secret_id: str,
    db: Session = Depends(get_db)
):
    """
    Mengambil detail order secret berdasarkan order_secret_id (ID dari marketplace).

    **No authentication required** - Endpoint ini public untuk customer

    **Path Parameter**:
    - `order_secret_id`: ID order dari marketplace (contoh: TBHJG65435O)

    **Use Case**: Customer scan QR code yang berisi order_secret_id untuk lihat/isi pesan secret
    """
    return get_order_secret_by_id(order_secret_id, db)


@router.put("/{order_secret_id}", summary="Update order secret (Customer fills message)")
def update(
    order_secret_id: str,
    data: OrderSecretUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update order secret - digunakan oleh customer untuk mengisi pesan secret.

    **No authentication required** - Endpoint ini public untuk customer

    **Path Parameter**:
    - `order_secret_id`: ID order dari marketplace (contoh: TBHJG65435O)

    **Request Body** (semua field optional):
    - `message`: Pesan dari customer kepada penerima
    - `emotional`: Status emosional (contoh: Senang, Bahagia, Haru)
    - `from_name`: Nama pengirim pesan

    **Auto-filled**:
    - `updated_by`: "Customizer Service" (karena diisi oleh customer, bukan admin)
    - `updated_at`: Timestamp otomatis

    **Use Case**: Customer mengisi form pesan secret setelah scan QR code
    """
    return update_order_secret(order_secret_id, data, db)


@router.delete("/{order_secret_id}", summary="Delete order secret")
def delete(
    order_secret_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Soft delete order secret (data tidak benar-benar dihapus).

    **Authentication required**: Bearer token dari login

    **Path Parameter**:
    - `order_secret_id`: ID order dari marketplace (contoh: TBHJG65435O)

    **Auto-filled**:
    - `deleted_by`: Email dari user yang login
    - `deleted_at`: Timestamp otomatis

    **Note**: Data hanya di-mark sebagai deleted, tidak benar-benar dihapus dari database

    **Use Case**: Admin menghapus order yang bermasalah atau dibatalkan
    """
    return delete_order_secret(order_secret_id, db, current_user)
