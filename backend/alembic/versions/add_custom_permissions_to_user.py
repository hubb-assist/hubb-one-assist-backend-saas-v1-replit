"""Add custom_permissions to User model

Revision ID: add_custom_permissions_user
Revises: 82847e247ea8
Create Date: 2025-05-13 01:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_custom_permissions_user'
down_revision = '82847e247ea8'
branch_labels = None
depends_on = None


def upgrade():
    # Adiciona a coluna custom_permissions à tabela users
    op.add_column('users', sa.Column('custom_permissions', sa.Text(), nullable=True))


def downgrade():
    # Remove a coluna custom_permissions da tabela users
    op.drop_column('users', 'custom_permissions')