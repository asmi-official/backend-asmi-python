from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config.deps import get_db, get_current_user, CurrentUser
from app.modules.business.schema import BusinessRegisterSchema, BusinessUpdateSchema
from app.modules.business.controller import BusinessController

router = APIRouter()


@router.post("/register", summary="Register new business and user")
def register(
    data: BusinessRegisterSchema,
    db: Session = Depends(get_db)
):
    return BusinessController.register_business(data, db)


@router.get("/my-businesses", summary="Get my businesses")
def get_my_business_list(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    return BusinessController.get_my_businesses(str(current_user.user_id), db)


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
    return BusinessController.get_businesses(
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
    return BusinessController.get_business_by_id(business_id, str(current_user.user_id), db)


@router.put("/{business_id}", summary="Update business and user")
def update_business_data(
    business_id: str,
    data: BusinessUpdateSchema,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    return BusinessController.update_business(business_id, data, db, current_user)
