"""create appointments table

Revision ID: g2j0dk0h4f51
Revises: h1i9cj9g3f50
Create Date: 2025-05-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'g2j0dk0h4f51'
down_revision = 'h1i9cj9g3f50'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'appointments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('subscriber_id', UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', UUID(as_uuid=True), nullable=False),
        sa.Column('provider_id', UUID(as_uuid=True), nullable=False),
        sa.Column('service_name', sa.String(255), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='scheduled'),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['subscriber_id'], ['subscribers.id']),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'])
    )
    
    # Criar índices para melhorar a performance das consultas frequentes
    op.create_index('idx_appointments_subscriber_id', 'appointments', ['subscriber_id'])
    op.create_index('idx_appointments_patient_id', 'appointments', ['patient_id'])
    op.create_index('idx_appointments_provider_id', 'appointments', ['provider_id'])
    op.create_index('idx_appointments_start_time', 'appointments', ['start_time'])
    op.create_index('idx_appointments_status', 'appointments', ['status'])
    op.create_index('idx_appointments_is_active', 'appointments', ['is_active'])


def downgrade():
    op.drop_index('idx_appointments_is_active')
    op.drop_index('idx_appointments_status')
    op.drop_index('idx_appointments_start_time')
    op.drop_index('idx_appointments_provider_id')
    op.drop_index('idx_appointments_patient_id')
    op.drop_index('idx_appointments_subscriber_id')
    op.drop_table('appointments')