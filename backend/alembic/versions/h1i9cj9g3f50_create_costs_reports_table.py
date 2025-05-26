"""create costs_reports table

Revision ID: h1i9cj9g3f50
Revises: f0g9ch8g2e49
Create Date: 2025-05-20 14:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'h1i9cj9g3f50'
down_revision = 'f0g9ch8g2e49'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'costs_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subscriber_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date_from', sa.Date(), nullable=False),
        sa.Column('date_to', sa.Date(), nullable=False),
        sa.Column('report_type', sa.String(50), nullable=False),
        sa.Column('total_fixed_costs', sa.Numeric(10, 2), nullable=False, default=0),
        sa.Column('total_variable_costs', sa.Numeric(10, 2), nullable=False, default=0),
        sa.Column('total_clinical_costs', sa.Numeric(10, 2), nullable=False, default=0),
        sa.Column('total_supplies_costs', sa.Numeric(10, 2), nullable=False, default=0),
        sa.Column('grand_total', sa.Numeric(10, 2), nullable=False, default=0),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_costs_reports_subscriber_id', 'costs_reports', ['subscriber_id'], unique=False)


def downgrade():
    op.drop_index('ix_costs_reports_subscriber_id', table_name='costs_reports')
    op.drop_table('costs_reports')