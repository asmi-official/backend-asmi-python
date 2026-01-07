from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config.deps import get_db, get_current_user, CurrentUser
from app.modules.order_secret.schema import (
    OrderSecretCreateSchema,
    OrderSecretUpdateSchema
)
from app.modules.order_secret.controller import OrderSecretController

router = APIRouter()


@router.post("/", summary="Create order secret")
def create(
    data: OrderSecretCreateSchema,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    return OrderSecretController.create_order_secret(data, db, current_user)


@router.get("/", summary="Get all order secrets")
def list_all(
    search: str = Query(
        None,
        description="Search by order_secret_id, message, emotional, from_name"
    ),
    sort_by: str = Query(
        None,
        description="Field untuk sorting (e.g., created_at, order_secret_id)",
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
    db: Session = Depends(get_db)
):
    return OrderSecretController.get_order_secrets(
        db=db,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page
    )


@router.get("/{order_secret_id}", summary="Get order secret by ID")
def get_by_id(
    order_secret_id: str,
    db: Session = Depends(get_db)
):
    return OrderSecretController.get_order_secret_by_id(order_secret_id, db)


@router.put("/{order_secret_id}", summary="Update order secret")
def update(
    order_secret_id: str,
    data: OrderSecretUpdateSchema,
    db: Session = Depends(get_db)
):
    return OrderSecretController.update_order_secret(order_secret_id, data, db)


@router.delete("/{order_secret_id}", summary="Delete order secret")
def delete(
    order_secret_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    return OrderSecretController.delete_order_secret(order_secret_id, db, current_user)
