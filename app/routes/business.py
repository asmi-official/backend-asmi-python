from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config.deps import get_db, get_current_user, CurrentUser
from app.schemas.business_schema import BusinessRegisterSchema, BusinessUpdateSchema
from app.controller.business_controller import (
    register_business,
    get_businesses,
    get_my_businesses,
    get_business_by_id,
    update_business
)

router = APIRouter()


@router.post("/register", summary="Register new business and user")
def register(
    data: BusinessRegisterSchema,
    db: Session = Depends(get_db)
):
    """
    Register business baru sekaligus create user (Public endpoint - No authentication required).

    Endpoint ini akan:
    1. Create user baru dengan role "merchen"
    2. Create business yang terhubung dengan user tersebut

    **User Credentials**:
    - `name`: Nama lengkap owner (required)
    - `username`: Username untuk login (required, unique)
    - `email`: Email user untuk login (required, unique)
    - `password`: Password untuk login (required, min 6 karakter)

    **Business Details**:
    - `business_name`: Nama legal usaha (required)
    - `shop_name`: Nama toko/brand (required)
    - `phone`: Nomor telepon bisnis (required)
    - `business_email`: Email bisnis (required)
    - `address`: Alamat lengkap bisnis (optional)
    - `business_type_id`: ID tipe bisnis (optional)

    **Auto-filled**:
    - `business_code`: Generate otomatis dengan format BUS000000000001
    - `user.role`: Default "merchen"
    - `business.status`: Default "trial"
    - `business.user_id`: Link ke user yang baru dibuat

    **Response**:
    - HTTP 201: User dan business berhasil dibuat
    - HTTP 400: Validation error (email/username sudah ada, dll)

    **Note**: Setelah register berhasil, user bisa langsung login menggunakan username/email dan password.
    """
    return register_business(data, db)


@router.get("/my-businesses", summary="Get my businesses")
def get_my_business_list(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get semua business milik user yang sedang login.

    **Authentication required**: Bearer token dari login

    **Response**:
    - List semua business yang dimiliki oleh user (tidak termasuk yang sudah dihapus)
    """
    return get_my_businesses(str(current_user.user_id), db)


@router.get("/", summary="Get all businesses")
def get_business_list(
    search: str = Query(
        None,
        description="Search by business_code, business_name, shop_name, email"
    ),
    sort_by: str = Query(
        None,
        description="Field untuk sorting (e.g., created_at, business_name)",
        example="created_at"
    ),
    sort_order: str = Query(
        "desc",
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
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get semua businesses dengan filter dan pagination (Admin only).

    **Authentication required**: Bearer token dari login

    **Query Parameters**:
    - `search`: Search by business_code, business_name, shop_name, email (optional)
    - `sort_by`: Field untuk sorting (default: created_at)
    - `sort_order`: Sort order asc/desc (default: desc)
    - `page`: Page number untuk pagination (optional)
    - `per_page`: Items per page (optional, max 100)

    **Response**:
    - List semua businesses yang tidak dihapus
    - Includes pagination meta if page/per_page provided

    **Examples**:
    - `/api/v1/businesses` - Get all
    - `/api/v1/businesses?search=Maju` - Search by keyword
    - `/api/v1/businesses?page=1&per_page=10` - Paginated results
    - `/api/v1/businesses?sort_by=business_name&sort_order=asc` - Sorted by name
    """
    return get_businesses(
        db=db,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page
    )


@router.get("/{business_id}", summary="Get business by ID")
def get_business_detail(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get detail business berdasarkan ID.

    **Authentication required**: Bearer token dari login

    **Path Parameter**:
    - `business_id`: UUID dari business

    **Note**: User hanya bisa mengakses business miliknya sendiri

    **Response**:
    - HTTP 200: Business detail
    - HTTP 404: Business not found atau bukan milik user
    """
    return get_business_by_id(business_id, str(current_user.user_id), db)


@router.put("/{business_id}", summary="Update business and user")
def update_business_data(
    business_id: str,
    data: BusinessUpdateSchema,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Update business dan user data sekaligus.

    **Authentication required**: Bearer token dari login

    **Path Parameter**:
    - `business_id`: UUID dari business

    **Request Body** (semua field optional):

    **User Fields** (akan update di tabel users):
    - `name`: Nama lengkap user/owner (akan update user.name dan business.name_owner)
    - `username`: Username untuk login (harus unique jika diubah)
    - `user_email`: Email user untuk login (harus unique jika diubah)

    **Business Fields**:
    - `business_name`: Nama legal usaha baru
    - `shop_name`: Nama toko/brand baru
    - `name_owner`: Nama pemilik baru
    - `phone`: Nomor telepon baru
    - `email`: Email bisnis baru (harus unique jika diubah)
    - `address`: Alamat baru
    - `business_type_id`: ID tipe bisnis baru
    - `status`: Status bisnis baru (trial, active, suspended)

    **Auto-filled**:
    - `updated_by`: Email user yang update
    - `updated_at`: Timestamp otomatis

    **Note**:
    - User hanya bisa update business miliknya sendiri
    - Update name akan otomatis update name_owner di business
    - Semua update dilakukan dalam satu transaction

    **Response**:
    - HTTP 200: Business dan user berhasil diupdate
    - HTTP 404: Business not found atau bukan milik user
    - HTTP 400: Validation error (email/username sudah dipakai, dll)
    """
    return update_business(business_id, data, db, current_user)
