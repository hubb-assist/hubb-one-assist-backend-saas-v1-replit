"""create appointments table

Revision ID: 20250520162755
Revises: h1i9cj9g3f50
Create Date: 2025-05-20 16:27:55.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


# revision identifiers, used by Alembic.
revision = '20250520162755'
down_revision = 'e8f7af6f0e47'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'appointments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('subscriber_id', UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', UUID(as_uuid=True), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('service_name', sa.String(255), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='scheduled'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['subscriber_id'], ['subscribers.id'], name='fk_appointment_subscriber'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], name='fk_appointment_patient'),
        sa.ForeignKeyConstraint(['provider_id'], ['users.id'], name='fk_appointment_provider'),
    )
    
    # Criar índice para busca de conflitos de horário
    op.create_index(
        'ix_appointments_provider_time', 
        'appointments', 
        ['provider_id', 'start_time', 'end_time']
    )


def downgrade():
    op.drop_index('ix_appointments_provider_time')
    op.drop_table('appointments')