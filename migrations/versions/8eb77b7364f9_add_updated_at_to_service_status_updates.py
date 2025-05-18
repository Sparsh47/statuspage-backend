"""add updated_at to service_status_updates

Revision ID: 8eb77b7364f9
Revises:
Create Date: 2025-05-18 16:52:31.155050

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8eb77b7364f9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('service_status_updates', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('service_status_updates', 'updated_at')
    # ### end Alembic commands ###
