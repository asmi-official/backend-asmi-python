"""fix_typo_merchen_to_merchant

Revision ID: 13761fb1bf49
Revises: cbcb36c259ea
Create Date: 2025-12-28 18:39:21.024058

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '13761fb1bf49'
down_revision: Union[str, Sequence[str], None] = 'cbcb36c259ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix typo in user role: merchen -> merchant."""
    # We can't add and use a new enum value in the same transaction
    # So we'll convert to text, update the data, then recreate the enum

    # Step 1: Convert column to text temporarily
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE TEXT")

    # Step 2: Update any users with role 'merchen' to 'merchant'
    op.execute("""
        UPDATE users
        SET role = 'merchant'
        WHERE role = 'merchen'
    """)

    # Step 3: Drop the old enum type
    op.execute("DROP TYPE user_role")

    # Step 4: Create the new enum type with correct values
    op.execute("CREATE TYPE user_role AS ENUM ('admin', 'merchant')")

    # Step 5: Convert the column back to use the enum type
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE user_role USING role::user_role")


def downgrade() -> None:
    """Revert fix (change merchant back to merchen)."""
    # Note: This is for rollback purposes only, normally you wouldn't want to revert a bug fix

    # Step 1: Convert column to text
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE TEXT")

    # Step 2: Drop the current enum type
    op.execute("DROP TYPE user_role")

    # Step 3: Create the old enum type with the typo
    op.execute("CREATE TYPE user_role AS ENUM ('admin', 'merchen')")

    # Step 4: Update users to use the typo
    op.execute("""
        UPDATE users
        SET role = 'merchen'
        WHERE role = 'merchant'
    """)

    # Step 5: Convert the column back to use the enum type
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE user_role USING role::user_role")
