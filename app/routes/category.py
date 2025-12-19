from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.deps import get_db, get_current_user, CurrentUser
from app.schemas.category_schema import (
    CategoryCreateSchema,
    CategoryUpdateSchema,
    CategoryResponseSchema
)
from app.controller.category_controller import (
    create_category,
    get_categories,
    update_category,
    delete_category
)

router = APIRouter()

@router.post("/", response_model=CategoryResponseSchema)
def create(
    data: CategoryCreateSchema,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    return create_category(data, db, current_user)

@router.get("/", response_model=list[CategoryResponseSchema])
def list_all(db: Session = Depends(get_db)):
    return get_categories(db)

@router.put("/{category_id}", response_model=CategoryResponseSchema)
def update(
    category_id: int,
    data: CategoryUpdateSchema,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    return update_category(category_id, data, db, current_user)

@router.delete("/{category_id}")
def delete(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    return delete_category(category_id, db, current_user)
