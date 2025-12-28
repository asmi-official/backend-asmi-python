"""remove_karyawan_role

Revision ID: 7eec19968c33
Revises: 13761fb1bf49
Create Date: 2025-12-28 18:43:41.670851

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7eec19968c33'
down_revision: Union[str, Sequence[str], None] = '13761fb1bf49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove 'karyawan' role from user_role enum and delete users with that role."""

    # Step 1: Convert column to text temporarily (so we can work with the data)
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE TEXT")

    # Step 2: Delete all users with role 'karyawan' (hard delete)
    op.execute("""
        DELETE FROM users
        WHERE role = 'karyawan'
    """)

    # Step 3: Drop the old enum type
    op.execute("DROP TYPE user_role")

    # Step 4: Create the new enum type without 'karyawan'
    op.execute("CREATE TYPE user_role AS ENUM ('admin', 'merchant')")

    # Step 5: Convert the column back to use the enum type
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE user_role USING role::user_role")


def downgrade() -> None:
    """Restore 'karyawan' role to user_role enum (data won't be restored)."""

    # Step 1: Convert column to text
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE TEXT")

    # Step 2: Drop the current enum type
    op.execute("DROP TYPE user_role")

    # Step 3: Create the old enum type with 'karyawan'
    op.execute("CREATE TYPE user_role AS ENUM ('admin', 'merchant', 'karyawan')")

    # Step 4: Convert the column back to use the enum type
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE user_role USING role::user_role")
