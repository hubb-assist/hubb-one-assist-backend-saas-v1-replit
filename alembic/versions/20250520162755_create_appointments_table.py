"""create_appointments_table

Revision ID: 20250520162755
Revises: h1i9cj9g3f50
Create Date: 2025-05-20 16:27:55.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '20250520162755'
down_revision = 'h1i9cj9g3f50'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'appointments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('subscriber_id', UUID(as_uuid=True), sa.ForeignKey('subscribers.id'), nullable=False, index=True),
        sa.Column('patient_id', UUID(as_uuid=True), sa.ForeignKey('patients.id'), nullable=False, index=True),
        sa.Column('provider_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('service_name', sa.String(255), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False, index=True),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='scheduled', index=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Adicionar índices para melhorar performance
    op.create_index('ix_appointments_subscriber_id', 'appointments', ['subscriber_id'], unique=False)
    op.create_index('ix_appointments_patient_id', 'appointments', ['patient_id'], unique=False)
    op.create_index('ix_appointments_provider_id', 'appointments', ['provider_id'], unique=False)
    op.create_index('ix_appointments_start_time', 'appointments', ['start_time'], unique=False)
    op.create_index('ix_appointments_status', 'appointments', ['status'], unique=False)


def downgrade():
    # Remover índices
    op.drop_index('ix_appointments_status', table_name='appointments')
    op.drop_index('ix_appointments_start_time', table_name='appointments')
    op.drop_index('ix_appointments_provider_id', table_name='appointments')
    op.drop_index('ix_appointments_patient_id', table_name='appointments')
    op.drop_index('ix_appointments_subscriber_id', table_name='appointments')
    
    # Remover tabela
    op.drop_table('appointments')