"""made updated_at non nullable in service_status_updates

Revision ID: bae811a7f5b7
Revises: None
Create Date: 2025-05-18 16:59:43.705537

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'bae811a7f5b7'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Fill NULL updated_at with current timestamp
    op.execute(
        "UPDATE service_status_updates SET updated_at = NOW() WHERE updated_at IS NULL"
    )

    # Alter column to be NOT NULL
    op.alter_column(
        'service_status_updates', 'updated_at',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'service_status_updates',
        'updated_at',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True
    )
