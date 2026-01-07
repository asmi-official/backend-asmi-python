from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config.deps import get_db, get_current_user, CurrentUser
from app.modules.master_type.schema import (
    MasterTypesCreateSchema,
    MasterTypesUpdateSchema
)
from app.modules.master_type.controller import MasterTypeController

router = APIRouter()


@router.post("/", summary="Create master type")
def create(
    data: MasterTypesCreateSchema,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    return MasterTypeController.create_master_type(data, db, current_user)


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
    return MasterTypeController.get_master_types(
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
    return MasterTypeController.get_master_type_by_id(master_type_id, db)


@router.put("/{master_type_id}", summary="Update master type")
def update(
    master_type_id: str,
    data: MasterTypesUpdateSchema,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    return MasterTypeController.update_master_type(master_type_id, data, db, current_user)


@router.delete("/{master_type_id}", summary="Delete master type")
def delete(
    master_type_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    return MasterTypeController.delete_master_type(master_type_id, db, current_user)
