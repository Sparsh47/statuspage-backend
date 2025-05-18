"""Merge heads 8eb77b7364f9 and bae811a7f5b7

Revision ID: 564835105fba
Revises: 8eb77b7364f9, bae811a7f5b7
Create Date: 2025-05-18 17:06:16.786631

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '564835105fba'
down_revision: Union[str, None] = ('8eb77b7364f9', 'bae811a7f5b7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
