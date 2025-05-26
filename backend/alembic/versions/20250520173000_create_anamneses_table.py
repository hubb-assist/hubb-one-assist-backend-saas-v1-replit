"""create anamneses table

Revision ID: 20250520173000
Revises: 20250520170000
Create Date: 2025-05-20 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid

revision = "20250520173000"
down_revision = "20250520170000"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "anamneses",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("subscriber_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("subscribers.id"), nullable=False),
        sa.Column("patient_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("chief_complaint", sa.Text(), nullable=False),
        sa.Column("medical_history", sa.Text(), nullable=True),
        sa.Column("allergies", sa.Text(), nullable=True),
        sa.Column("medications", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_anamneses_patient", "anamneses", ["patient_id"])

def downgrade():
    op.drop_index("ix_anamneses_patient", table_name="anamneses")
    op.drop_table("anamneses")