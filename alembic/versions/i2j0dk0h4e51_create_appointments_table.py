"""create appointments table

Revision ID: i2j0dk0h4e51
Revises: h1i9cj9g3f50
Create Date: 2025-05-20 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'i2j0dk0h4e51'
down_revision = 'h1i9cj9g3f50'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "appointments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("subscriber_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subscribers.id"), nullable=False),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("provider_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("service_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="scheduled"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    # índice para busca rápida por provider e intervalo
    op.create_index("ix_appointments_provider_time", "appointments", ["provider_id", "start_time", "end_time"])


def downgrade():
    op.drop_index("ix_appointments_provider_time", table_name="appointments")
    op.drop_table("appointments")