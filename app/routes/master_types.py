from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config.deps import get_db, get_current_user, CurrentUser
from app.schemas.master_types_schema import (
    MasterTypesCreateSchema,
    MasterTypesUpdateSchema
)
from app.controller.master_types_controller import (
    create_master_type,
    get_master_types,
    get_master_type_by_id,
    update_master_type,
    delete_master_type
)

router = APIRouter()


@router.post("/", summary="Create master type")
def create(
    data: MasterTypesCreateSchema,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Create master type baru (Admin only).

    **Authentication required**: Bearer token dari login dengan role admin

    **Authorization**: Only admin users can create master types

    **Request Body**:
    - `group_code`: Group code (BUSINESS, PRODUCT, ORDER, USER) - required
    - `code`: Kode unik max 5 karakter - required, unique
    - `name`: Nama lengkap - required
    - `description`: Deskripsi - optional
    - `is_active`: Status aktif - default True

    **Auto-filled**:
    - `created_by`: Email user yang membuat
    - `created_at`: Timestamp otomatis

    **Response**:
    - HTTP 201: Master type berhasil dibuat
    - HTTP 403: Forbidden jika user bukan admin
    - HTTP 400: Validation error (code sudah ada, dll)
    - HTTP 401: Unauthorized
    """
    return create_master_type(data, db, current_user)


@router.get("/", summary="Get all master types")
def list_all(
    search: str = Query(
        None,
        description="Search by code, name, atau description"
    ),
    sort_by: str = Query(
        None,
        description="Field untuk sorting (e.g., group_code, code, name)",
        example="group_code"
    ),
    sort_order: str = Query(
        "asc",
        description="Sort order: asc atau desc",
        enum=["asc", "desc"]
    ),
    page: int = Query(
        None,
        description="Page number (1-based)",
        ge=1
    ),
    per_page: int = Query(
        None,
        description="Items per page",
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db)
):
    """
    Get semua master types dengan filter optional (Public - No authentication required).

    **Query Parameters**:
    - `search`: Search by code, name, atau description (optional)
    - `sort_by`: Field untuk sorting (default: group_code)
    - `sort_order`: Sort order asc/desc (default: asc)
    - `page`: Page number untuk pagination (optional)
    - `per_page`: Items per page (optional, max 100)

    **Response**:
    - List semua master types yang tidak dihapus
    - Sorted by group_code dan code (default)
    - Includes pagination meta if page/per_page provided

    **Examples**:
    - `/api/v1/master-types` - Get all
    - `/api/v1/master-types?search=ASMI` - Search by keyword
    - `/api/v1/master-types?page=1&per_page=10` - Paginated results
    - `/api/v1/master-types?sort_by=name&sort_order=desc` - Sorted by name descending
    """
    return get_master_types(
        db=db,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page
    )


@router.get("/{master_type_id}", summary="Get master type by ID")
def get_by_id(
    master_type_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detail master type by ID (Public - No authentication required).

    **Path Parameter**:
    - `master_type_id`: UUID master type

    **Response**:
    - HTTP 200: Master type detail
    - HTTP 404: Master type not found
    """
    return get_master_type_by_id(master_type_id, db)


@router.put("/{master_type_id}", summary="Update master type")
def update(
    master_type_id: str,
    data: MasterTypesUpdateSchema,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Update master type (Admin only).

    **Authentication required**: Bearer token dari login dengan role admin

    **Authorization**: Only admin users can update master types

    **Path Parameter**:
    - `master_type_id`: UUID master type

    **Request Body** (semua field optional):
    - `group_code`: Group code baru
    - `code`: Kode baru (harus unique jika diubah)
    - `name`: Nama baru
    - `description`: Deskripsi baru
    - `is_active`: Status aktif baru

    **Auto-filled**:
    - `updated_by`: Email user yang update
    - `updated_at`: Timestamp otomatis

    **Response**:
    - HTTP 200: Master type berhasil diupdate
    - HTTP 403: Forbidden jika user bukan admin
    - HTTP 404: Master type not found
    - HTTP 401: Unauthorized
    """
    return update_master_type(master_type_id, data, db, current_user)


@router.delete("/{master_type_id}", summary="Delete master type")
def delete(
    master_type_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Soft delete master type (Admin only).

    **Authentication required**: Bearer token dari login dengan role admin

    **Authorization**: Only admin users can delete master types

    **Path Parameter**:
    - `master_type_id`: UUID master type

    **Auto-filled**:
    - `deleted_by`: Email user yang menghapus
    - `deleted_at`: Timestamp otomatis

    **Response**:
    - HTTP 200: Master type berhasil dihapus
    - HTTP 403: Forbidden jika user bukan admin
    - HTTP 404: Master type not found
    - HTTP 401: Unauthorized

    **Note**: Data hanya di-mark sebagai deleted (soft delete)
    """
    return delete_master_type(master_type_id, db, current_user)
