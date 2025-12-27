"""replace unique constraint with partial index for soft delete

Revision ID: f8a1b2c3d4e5
Revises: eaae7a12e839
Create Date: 2025-12-27 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8a1b2c3d4e5'
down_revision: Union[str, Sequence[str], None] = 'a81cc8b0758a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Replace the unique constraint on category_marketplaces.name with a partial unique index
    that only applies to non-deleted records (where deleted_at IS NULL).

    This allows reusing the same name after soft delete.
    """
    # Drop the existing unique constraint
    op.drop_constraint('category_marketplaces_name_key', 'category_marketplaces', type_='unique')

    # Create a partial unique index that only applies to non-deleted records
    op.create_index(
        'idx_category_marketplaces_name_unique_not_deleted',
        'category_marketplaces',
        ['name'],
        unique=True,
        postgresql_where=sa.text('deleted_at IS NULL')
    )


def downgrade() -> None:
    """Downgrade: restore the simple unique constraint."""
    # Drop the partial unique index
    op.drop_index('idx_category_marketplaces_name_unique_not_deleted', 'category_marketplaces')

    # Restore the simple unique constraint
    op.create_unique_constraint('category_marketplaces_name_key', 'category_marketplaces', ['name'])
