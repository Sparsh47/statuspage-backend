"""modified fields of organization model

Revision ID: d8357f0bf0bb
Revises: 564835105fba
Create Date: 2025-05-18 18:19:47.797903

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8357f0bf0bb'
down_revision: Union[str, None] = '564835105fba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Step 1: Drop foreign key constraints referencing organizations.id
    op.drop_constraint('users_organization_id_fkey', 'users', type_='foreignkey')
    op.drop_constraint('teams_organization_id_fkey', 'teams', type_='foreignkey')

    # Step 2: Alter organizations.id to VARCHAR and remove the sequence default
    op.alter_column('organizations', 'id',
                    existing_type=sa.INTEGER(),
                    type_=sa.String(),
                    nullable=False,
                    server_default=None)  # Remove sequence default

    # Step 3: Alter users.organization_id to VARCHAR
    op.alter_column('users', 'organization_id',
                    existing_type=sa.INTEGER(),
                    type_=sa.String(),
                    nullable=True)  # Adjust nullable based on your schema

    # Step 4: Alter teams.organization_id to VARCHAR
    op.alter_column('teams', 'organization_id',
                    existing_type=sa.INTEGER(),
                    type_=sa.String(),
                    nullable=True)  # Adjust nullable based on your schema

    # Step 5: Recreate foreign key constraints
    op.create_foreign_key('users_organization_id_fkey', 'users', 'organizations',
                          ['organization_id'], ['id'])
    op.create_foreign_key('teams_organization_id_fkey', 'teams', 'organizations',
                          ['organization_id'], ['id'])

    # Step 6: Drop the sequence if no longer needed
    op.execute('DROP SEQUENCE IF EXISTS organizations_id_seq')


def downgrade() -> None:
    """Downgrade schema."""
    # Step 1: Drop foreign key constraints
    op.drop_constraint('users_organization_id_fkey', 'users', type_='foreignkey')
    op.drop_constraint('teams_organization_id_fkey', 'teams', type_='foreignkey')

    # Step 2: Recreate the sequence for organizations.id
    op.execute('CREATE SEQUENCE organizations_id_seq')

    # Step 3: Alter users.organization_id back to INTEGER
    op.alter_column('users', 'organization_id',
                    existing_type=sa.String(),
                    type_=sa.INTEGER(),
                    nullable=True)  # Adjust nullable based on your schema

    # Step 4: Alter teams.organization_id back to INTEGER
    op.alter_column('teams', 'organization_id',
                    existing_type=sa.String(),
                    type_=sa.INTEGER(),
                    nullable=True)  # Adjust nullable based on your schema

    # Step 5: Alter organizations.id back to INTEGER and restore sequence default
    op.alter_column('organizations', 'id',
                    existing_type=sa.String(),
                    type_=sa.INTEGER(),
                    nullable=False,
                    server_default=sa.text("nextval('organizations_id_seq'::regclass)"))

    # Step 6: Recreate foreign key constraints
    op.create_foreign_key('users_organization_id_fkey', 'users', 'organizations',
                          ['organization_id'], ['id'])
    op.create_foreign_key('teams_organization_id_fkey', 'teams', 'organizations',
                          ['organization_id'], ['id'])