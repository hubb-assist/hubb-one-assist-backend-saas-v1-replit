"""create costs_variable table

Revision ID: e9f8bg7f1e48
Revises: e8f7af6f0e47
Create Date: 2025-05-20 13:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid
from sqlalchemy.dialects import postgresql


revision = "e9f8bg7f1e48"
down_revision = "e8f7af6f0e47"  # Revisão anterior (custos fixos)
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "costs_variable",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("subscriber_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subscribers.id"), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("valor_unitario", sa.Numeric(12, 2), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade():
    op.drop_table("costs_variable")