from sqlalchemy.orm import Session

from app.models.category import Category
from app.utils.db_validators import auto_validate
from app.core.exceptions import NotFoundException
from app.config.deps import CurrentUser


def create_category(data, db: Session, current_user: CurrentUser):
    # Auto-validate unique fields (name) berdasarkan model
    auto_validate(
        model=Category,
        data=data.model_dump(),
        db=db
    )

    category = Category(
        name=data.name,
        description=data.description,
        created_by=current_user.email
    )

    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_categories(db: Session):
    return db.query(Category).filter(Category.deleted_at.is_(None)).order_by(Category.id.desc()).all()


def update_category(category_id: int, data, db: Session, current_user: CurrentUser):
    # Cari category yang tidak terhapus
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.deleted_at.is_(None)
    ).first()
    if not category:
        raise NotFoundException(
            message="Category not found",
            details={"category_id": category_id}
        )

    # Auto-validate unique fields, exclude current category ID
    auto_validate(
        model=Category,
        data=data.model_dump(exclude_unset=True),
        db=db,
        exclude_id=category_id
    )

    # Update fields jika ada
    if data.name is not None:
        category.name = data.name
    if data.description is not None:
        category.description = data.description

    # Set updated_by
    category.updated_by = current_user.email

    db.commit()
    db.refresh(category)
    return category


def delete_category(category_id: int, db: Session, current_user: CurrentUser):
    # Cari category yang tidak terhapus
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.deleted_at.is_(None)
    ).first()
    if not category:
        raise NotFoundException(
            message="Category not found",
            details={"category_id": category_id}
        )

    # Soft delete - set deleted_at timestamp dan deleted_by
    from datetime import datetime
    category.deleted_at = datetime.now()
    category.deleted_by = current_user.email

    db.commit()
    return {"message": "Category deleted successfully"}
