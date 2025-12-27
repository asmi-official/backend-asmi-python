"""
Dynamic Query Builder Utility
Provides reusable filtering, searching, and sorting functionality with JOIN support
"""

from typing import Type, Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Query, Session, joinedload
from sqlalchemy import or_, desc, asc


def apply_filters(
    query: Query,
    model: Type,
    filters: Optional[List[Dict[str, Any]]] = None
) -> Query:
    """
    Apply dynamic filters to a SQLAlchemy query

    Args:
        query: SQLAlchemy query object
        model: SQLAlchemy model class
        filters: List of filter objects [{"key": "field_name", "operator": "equal", "value": "value"}]

    Returns:
        Modified query with filters applied

    Supported operators:
        - equal, not_equal
        - like, contains, starts_with, ends_with
        - gt, gte, lt, lte
        - in, not_in
        - is_null, is_not_null
    """
    if not filters:
        return query

    for filter_item in filters:
        key = filter_item.get("key")
        operator = filter_item.get("operator", "equal")
        value = filter_item.get("value")

        # Skip jika key tidak ada di model
        if not hasattr(model, key):
            continue

        field = getattr(model, key)

        # Apply operator
        if operator == "equal":
            query = query.filter(field == value)
        elif operator == "not_equal":
            query = query.filter(field != value)
        elif operator == "like" or operator == "contains":
            query = query.filter(field.ilike(f"%{value}%"))
        elif operator == "starts_with":
            query = query.filter(field.ilike(f"{value}%"))
        elif operator == "ends_with":
            query = query.filter(field.ilike(f"%{value}"))
        elif operator == "gt":
            query = query.filter(field > value)
        elif operator == "gte":
            query = query.filter(field >= value)
        elif operator == "lt":
            query = query.filter(field < value)
        elif operator == "lte":
            query = query.filter(field <= value)
        elif operator == "in":
            if isinstance(value, list):
                query = query.filter(field.in_(value))
        elif operator == "not_in":
            if isinstance(value, list):
                query = query.filter(~field.in_(value))
        elif operator == "is_null":
            query = query.filter(field.is_(None))
        elif operator == "is_not_null":
            query = query.filter(field.isnot(None))

    return query


def apply_search(
    query: Query,
    model: Type,
    search: Optional[str] = None,
    search_fields: Optional[List[str]] = None
) -> Query:
    """
    Apply global search to specific fields

    Args:
        query: SQLAlchemy query object
        model: SQLAlchemy model class
        search: Search string
        search_fields: List of field names to search in

    Returns:
        Modified query with search applied
    """
    if not search or not search_fields:
        return query

    search_conditions = []
    for field_name in search_fields:
        if hasattr(model, field_name):
            field = getattr(model, field_name)
            search_conditions.append(field.ilike(f"%{search}%"))

    if search_conditions:
        query = query.filter(or_(*search_conditions))

    return query


def apply_sorting(
    query: Query,
    model: Type,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
    default_sort_field: str = "created_at"
) -> Query:
    """
    Apply dynamic sorting to query

    Args:
        query: SQLAlchemy query object
        model: SQLAlchemy model class
        sort_by: Field name to sort by
        sort_order: "asc" or "desc" (default: desc)
        default_sort_field: Default field to sort by if sort_by is not provided

    Returns:
        Modified query with sorting applied
    """
    # Use provided sort_by or fall back to default
    field_name = sort_by if sort_by and hasattr(model, sort_by) else default_sort_field

    if hasattr(model, field_name):
        sort_field = getattr(model, field_name)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))

    return query


def build_dynamic_query(
    db: Session,
    model: Type,
    search: Optional[str] = None,
    search_fields: Optional[List[str]] = None,
    filters: Optional[List[Dict[str, Any]]] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
    default_sort_field: str = "created_at",
    include_deleted: bool = False,
    joins: Optional[List[Dict[str, Any]]] = None,
    auto_search_all_fields: bool = False
) -> Query:
    """
    Build a complete query with filtering, searching, sorting, and JOIN support

    Args:
        db: Database session
        model: SQLAlchemy model class
        search: Search string
        search_fields: List of field names to search in (supports "Model.field" for joined tables)
                      If None and auto_search_all_fields=True, will search all string fields
        filters: List of filter objects (supports "key": "Model.field" for joined tables)
        sort_by: Field name to sort by (supports "Model.field" for joined tables)
        sort_order: "asc" or "desc"
        default_sort_field: Default sort field
        include_deleted: Whether to include soft-deleted records (default: False)
        joins: List of join configurations
            Format: [
                {
                    "model": CategoryMarketplace,
                    "condition": OrderSecret.category_marketplace_id == CategoryMarketplace.id,
                    "relationship": "category_marketplace",  # Optional: for eager loading
                    "load_only": ["id", "name", "description"]  # Optional: fields to load
                }
            ]
        auto_search_all_fields: If True, automatically search all string/text fields from model and joins

    Returns:
        Configured SQLAlchemy query ready to execute

    Example without JOIN:
        query = build_dynamic_query(
            db=db,
            model=OrderSecret,
            search="TikTok",
            search_fields=["order_secret_id", "created_by"],
            filters=[{"key": "emotional", "operator": "equal", "value": "Senang"}],
            sort_by="created_at",
            sort_order="desc"
        )

    Example with JOIN:
        query = build_dynamic_query(
            db=db,
            model=OrderSecret,
            search="TikTok",
            search_fields=["order_secret_id", "created_by", "CategoryMarketplace.name"],
            filters=[
                {"key": "emotional", "operator": "equal", "value": "Senang"},
                {"key": "CategoryMarketplace.name", "operator": "like", "value": "TikTok"}
            ],
            sort_by="CategoryMarketplace.name",
            sort_order="asc",
            joins=[
                {
                    "model": CategoryMarketplace,
                    "condition": OrderSecret.category_marketplace_id == CategoryMarketplace.id,
                    "relationship": "category_marketplace",
                    "load_only": ["id", "name", "description"]
                }
            ]
        )
    """
    # Start with base query
    query = db.query(model)

    # Filter out soft-deleted records if model has deleted_at field
    if not include_deleted and hasattr(model, 'deleted_at'):
        query = query.filter(model.deleted_at.is_(None))

    # Apply JOINs if provided
    joined_models = {}
    relationship_to_model = {}  # Map relationship name to model (e.g., "category_marketplace" -> CategoryMarketplace)

    if joins:
        for join_config in joins:
            join_model = join_config["model"]
            join_condition = join_config["condition"]

            # Add JOIN
            query = query.join(join_model, join_condition)

            # Store joined model for later reference by class name
            joined_models[join_model.__name__] = join_model

            # Also store by relationship name if provided (for frontend-friendly notation)
            if "relationship" in join_config:
                relationship_to_model[join_config["relationship"]] = join_model

            # Filter out soft-deleted from joined table if applicable
            if not include_deleted and hasattr(join_model, 'deleted_at'):
                query = query.filter(join_model.deleted_at.is_(None))

            # Apply eager loading with load_only if relationship is specified
            if "relationship" in join_config:
                relationship_name = join_config["relationship"]
                if "load_only" in join_config:
                    from sqlalchemy.orm import joinedload
                    load_only_fields = [getattr(join_model, field) for field in join_config["load_only"]]
                    query = query.options(
                        joinedload(getattr(model, relationship_name)).load_only(*load_only_fields)
                    )
                else:
                    from sqlalchemy.orm import joinedload
                    query = query.options(joinedload(getattr(model, relationship_name)))

    # Auto-discover searchable fields if enabled
    if auto_search_all_fields and search and not search_fields:
        from sqlalchemy import String, Text
        search_fields = []

        # Get string fields from main model
        for column in model.__table__.columns:
            if isinstance(column.type, (String, Text)):
                search_fields.append(column.name)

        # Get string fields from joined models
        for joined_model in relationship_to_model.values():
            for column in joined_model.__table__.columns:
                if isinstance(column.type, (String, Text)):
                    search_fields.append(column.name)

    # Apply search (with JOIN support)
    query = apply_search_with_joins(query, model, search, search_fields, joined_models, relationship_to_model)

    # Apply filters (with JOIN support)
    query = apply_filters_with_joins(query, model, filters, joined_models, relationship_to_model)

    # Apply sorting (with JOIN support)
    query = apply_sorting_with_joins(query, model, sort_by, sort_order, default_sort_field, joined_models, relationship_to_model)

    return query


def apply_search_with_joins(
    query: Query,
    model: Type,
    search: Optional[str] = None,
    search_fields: Optional[List[str]] = None,
    joined_models: Optional[Dict[str, Type]] = None,
    relationship_to_model: Optional[Dict[str, Type]] = None
) -> Query:
    """
    Apply global search to specific fields (supports joined table fields)

    Args:
        query: SQLAlchemy query object
        model: SQLAlchemy model class
        search: Search string
        search_fields: List of field names to search in
                      Supports both "ModelName.field" and "relationship_name.field" formats
        joined_models: Dict of joined model class names to model classes
        relationship_to_model: Dict of relationship names to model classes

    Returns:
        Modified query with search applied
    """
    if not search or not search_fields:
        return query

    if joined_models is None:
        joined_models = {}
    if relationship_to_model is None:
        relationship_to_model = {}

    search_conditions = []
    for field_name in search_fields:
        # Check if it's a joined table field (e.g., "CategoryMarketplace.name" or "category_marketplace.name")
        if "." in field_name:
            prefix, column_name = field_name.split(".", 1)

            # Try to find the model - check both class name and relationship name
            joined_model = None
            if prefix in joined_models:
                # Class name format (e.g., "CategoryMarketplace.name")
                joined_model = joined_models[prefix]
            elif prefix in relationship_to_model:
                # Relationship name format (e.g., "category_marketplace.name")
                joined_model = relationship_to_model[prefix]

            if joined_model and hasattr(joined_model, column_name):
                field = getattr(joined_model, column_name)
                search_conditions.append(field.ilike(f"%{search}%"))
        else:
            # Try main model first
            if hasattr(model, field_name):
                field = getattr(model, field_name)
                search_conditions.append(field.ilike(f"%{search}%"))
            else:
                # Field not in main model - search in joined models
                for joined_model in relationship_to_model.values():
                    if hasattr(joined_model, field_name):
                        field = getattr(joined_model, field_name)
                        search_conditions.append(field.ilike(f"%{search}%"))
                        break  # Only add once even if multiple joins have the same field

    if search_conditions:
        query = query.filter(or_(*search_conditions))

    return query


def apply_filters_with_joins(
    query: Query,
    model: Type,
    filters: Optional[List[Dict[str, Any]]] = None,
    joined_models: Optional[Dict[str, Type]] = None,
    relationship_to_model: Optional[Dict[str, Type]] = None
) -> Query:
    """
    Apply dynamic filters to a SQLAlchemy query (supports joined table fields)

    Args:
        query: SQLAlchemy query object
        model: SQLAlchemy model class
        filters: List of filter objects
                Supports both "ModelName.field" and "relationship_name.field" formats in "key"
        joined_models: Dict of joined model class names to model classes
        relationship_to_model: Dict of relationship names to model classes

    Returns:
        Modified query with filters applied
    """
    if not filters:
        return query

    if joined_models is None:
        joined_models = {}
    if relationship_to_model is None:
        relationship_to_model = {}

    for filter_item in filters:
        key = filter_item.get("key")
        operator = filter_item.get("operator", "equal")
        value = filter_item.get("value")

        # Check if it's a joined table field
        if "." in key:
            prefix, column_name = key.split(".", 1)

            # Try to find the model - check both class name and relationship name
            joined_model = None
            if prefix in joined_models:
                # Class name format (e.g., "CategoryMarketplace.name")
                joined_model = joined_models[prefix]
            elif prefix in relationship_to_model:
                # Relationship name format (e.g., "category_marketplace.name")
                joined_model = relationship_to_model[prefix]

            if not joined_model or not hasattr(joined_model, column_name):
                continue

            field = getattr(joined_model, column_name)
        else:
            # Try main model first
            if hasattr(model, key):
                field = getattr(model, key)
            else:
                # Field not in main model - search in joined models
                field = None
                for joined_model in relationship_to_model.values():
                    if hasattr(joined_model, key):
                        field = getattr(joined_model, key)
                        break  # Use first match

                if field is None:
                    continue  # Field not found in any model

        # Apply operator
        if operator == "equal":
            query = query.filter(field == value)
        elif operator == "not_equal":
            query = query.filter(field != value)
        elif operator == "like" or operator == "contains":
            query = query.filter(field.ilike(f"%{value}%"))
        elif operator == "starts_with":
            query = query.filter(field.ilike(f"{value}%"))
        elif operator == "ends_with":
            query = query.filter(field.ilike(f"%{value}"))
        elif operator == "gt":
            query = query.filter(field > value)
        elif operator == "gte":
            query = query.filter(field >= value)
        elif operator == "lt":
            query = query.filter(field < value)
        elif operator == "lte":
            query = query.filter(field <= value)
        elif operator == "in":
            if isinstance(value, list):
                query = query.filter(field.in_(value))
        elif operator == "not_in":
            if isinstance(value, list):
                query = query.filter(~field.in_(value))
        elif operator == "is_null":
            query = query.filter(field.is_(None))
        elif operator == "is_not_null":
            query = query.filter(field.isnot(None))

    return query


def apply_sorting_with_joins(
    query: Query,
    model: Type,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
    default_sort_field: str = "created_at",
    joined_models: Optional[Dict[str, Type]] = None,
    relationship_to_model: Optional[Dict[str, Type]] = None
) -> Query:
    """
    Apply dynamic sorting to query (supports joined table fields)

    Args:
        query: SQLAlchemy query object
        model: SQLAlchemy model class
        sort_by: Field name to sort by
                Supports both "ModelName.field" and "relationship_name.field" formats
        sort_order: "asc" or "desc" (default: desc)
        default_sort_field: Default field to sort by if sort_by is not provided
        joined_models: Dict of joined model class names to model classes
        relationship_to_model: Dict of relationship names to model classes

    Returns:
        Modified query with sorting applied
    """
    if joined_models is None:
        joined_models = {}
    if relationship_to_model is None:
        relationship_to_model = {}

    # Determine the field to sort by
    field_name = sort_by if sort_by else default_sort_field
    sort_field = None

    # Check if it's a joined table field
    if "." in field_name:
        prefix, column_name = field_name.split(".", 1)

        # Try to find the model - check both class name and relationship name
        joined_model = None
        if prefix in joined_models:
            # Class name format (e.g., "CategoryMarketplace.name")
            joined_model = joined_models[prefix]
        elif prefix in relationship_to_model:
            # Relationship name format (e.g., "category_marketplace.name")
            joined_model = relationship_to_model[prefix]

        if joined_model and hasattr(joined_model, column_name):
            sort_field = getattr(joined_model, column_name)
    else:
        # Try main model first
        if hasattr(model, field_name):
            sort_field = getattr(model, field_name)
        else:
            # Field not in main model - search in joined models
            for joined_model in relationship_to_model.values():
                if hasattr(joined_model, field_name):
                    sort_field = getattr(joined_model, field_name)
                    break  # Use first match

    # Apply sorting if field was found
    if sort_field is not None:
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))

    return query
