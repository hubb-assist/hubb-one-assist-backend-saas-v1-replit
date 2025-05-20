"""create payables and receivables tables

Revision ID: 20250520170000
Revises: 04139d2b5e14
Create Date: 2025-05-20 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid

# revisão deste arquivo
revision = "20250520170000"
down_revision = "04139d2b5e14"
branch_labels = None
depends_on = None

def upgrade():
    # Tabela payables
    op.create_table(
        "payables",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("subscriber_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("subscribers.id"), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("paid", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("payment_date", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    # Tabela receivables
    op.create_table(
        "receivables",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("subscriber_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("subscribers.id"), nullable=False),
        sa.Column("patient_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("received", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("receive_date", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    # Índices
    op.create_index("ix_payables_due_date", "payables", ["due_date"])
    op.create_index("ix_receivables_due_date", "receivables", ["due_date"])

def downgrade():
    op.drop_index("ix_receivables_due_date", table_name="receivables")
    op.drop_index("ix_payables_due_date", table_name="payables")
    op.drop_table("receivables")
    op.drop_table("payables")