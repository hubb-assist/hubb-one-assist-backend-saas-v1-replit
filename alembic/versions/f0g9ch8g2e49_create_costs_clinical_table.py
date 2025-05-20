"""create costs_clinical table

Revision ID: f0g9ch8g2e49
Revises: e9f8bg7f1e48
Create Date: 2025-05-20 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid
from sqlalchemy.dialects import postgresql


revision = "f0g9ch8g2e49"
down_revision = "e9f8bg7f1e48"  # Revisão anterior (custos variáveis)
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "costs_clinical",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("subscriber_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subscribers.id"), nullable=False),
        sa.Column("procedure_name", sa.String(length=255), nullable=False),
        sa.Column("duration_hours", sa.Numeric(5, 2), nullable=False),
        sa.Column("hourly_rate", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade():
    op.drop_table("costs_clinical")