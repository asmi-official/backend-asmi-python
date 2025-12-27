from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config.deps import get_db, get_current_user, CurrentUser
from app.schemas.category_marketplace_schema import (
    CategoryMarketplaceCreateSchema,
    CategoryMarketplaceUpdateSchema
)
from app.controller.category_marketplace_controller import (
    create_category_marketplace,
    get_category_marketplaces,
    get_category_marketplace_by_id,
    update_category_marketplace,
    delete_category_marketplace
)

router = APIRouter()


@router.post("/", summary="Create category marketplace")
def create(
    data: CategoryMarketplaceCreateSchema,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Membuat category marketplace baru (TikTok, Shopee, Tokopedia, dll).

    **Authentication required**: Bearer token dari login

    **Validations**:
    - `name` harus unique (tidak boleh duplikat dengan data yang belum dihapus)
    - `description` optional

    **Auto-filled**:
    - `created_by`: Email dari user yang login
    - `created_at`: Timestamp otomatis
    """
    return create_category_marketplace(data, db, current_user)


@router.get("/")
def list_all(
    search: str = Query(
        None,
        description="Global search di semua string fields (name, description, created_by, updated_by)",
        example="tiktok"
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
    Mengambil semua category marketplaces dengan search dan pagination.

    Query Parameters:
    - search: Global search (name, description, dll - otomatis semua string fields)
    - page: Page number (1-based, optional)
    - per_page: Items per page (optional)

    Response with pagination:
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

    Examples:
    - /api/v1/category-marketplaces?search=tiktok
    - /api/v1/category-marketplaces?page=1&per_page=10
    - /api/v1/category-marketplaces?search=shopee&page=2&per_page=20
    """
    return get_category_marketplaces(db, search, page, per_page)


@router.get("/{category_marketplace_id}", summary="Get category marketplace by ID")
def get_by_id(
    category_marketplace_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Mengambil detail category marketplace berdasarkan UUID ID.

    **Authentication required**: Bearer token dari login

    **Path Parameter**:
    - `category_marketplace_id`: UUID dari category marketplace
    """
    return get_category_marketplace_by_id(category_marketplace_id, db)


@router.put("/{category_marketplace_id}", summary="Update category marketplace")
def update(
    category_marketplace_id: str,
    data: CategoryMarketplaceUpdateSchema,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Update category marketplace (nama atau deskripsi).

    **Authentication required**: Bearer token dari login

    **Path Parameter**:
    - `category_marketplace_id`: UUID dari category marketplace

    **Request Body** (semua field optional):
    - `name`: Nama marketplace baru (harus unique)
    - `description`: Deskripsi baru

    **Auto-filled**:
    - `updated_by`: Email dari user yang login
    - `updated_at`: Timestamp otomatis
    """
    return update_category_marketplace(category_marketplace_id, data, db, current_user)


@router.delete("/{category_marketplace_id}", summary="Delete category marketplace")
def delete(
    category_marketplace_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Soft delete category marketplace (data tidak benar-benar dihapus).

    **Authentication required**: Bearer token dari login

    **Path Parameter**:
    - `category_marketplace_id`: UUID dari category marketplace

    **Auto-filled**:
    - `deleted_by`: Email dari user yang login
    - `deleted_at`: Timestamp otomatis

    **Note**: Data hanya di-mark sebagai deleted, tidak benar-benar dihapus dari database
    """
    return delete_category_marketplace(category_marketplace_id, db, current_user)
