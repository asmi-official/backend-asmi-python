from fastapi import APIRouter, Depends
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


@router.post("/")
def create(
    data: CategoryMarketplaceCreateSchema,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Membuat category marketplace baru (tiktok, shopee, dll).
    Requires authentication.
    """
    return create_category_marketplace(data, db, current_user)


@router.get("/")
def list_all(
    search: str = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Mengambil semua category marketplaces yang tidak dihapus.
    Optional query parameter 'search' untuk mencari berdasarkan name (case-insensitive).
    Requires authentication.

    Example: /api/v1/category-marketplaces?search=tiktok
    """
    return get_category_marketplaces(db, search)


@router.get("/{category_marketplace_id}")
def get_by_id(
    category_marketplace_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Mengambil detail category marketplace berdasarkan ID.
    Requires authentication.
    """
    return get_category_marketplace_by_id(category_marketplace_id, db)


@router.put("/{category_marketplace_id}")
def update(
    category_marketplace_id: str,
    data: CategoryMarketplaceUpdateSchema,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Update category marketplace.
    Requires authentication.
    """
    return update_category_marketplace(category_marketplace_id, data, db, current_user)


@router.delete("/{category_marketplace_id}")
def delete(
    category_marketplace_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Soft delete category marketplace.
    Requires authentication.
    """
    return delete_category_marketplace(category_marketplace_id, db, current_user)
