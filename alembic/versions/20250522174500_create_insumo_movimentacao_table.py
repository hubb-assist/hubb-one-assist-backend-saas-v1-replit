"""create insumo_movimentacao table

Revision ID: 20250522174500
Revises: 20250520173000
Create Date: 2025-05-22 17:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '20250522174500'
down_revision: Union[str, None] = '20250520173000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Cria tabela de histórico de movimentações de estoque de insumos
    op.create_table(
        'insumo_movimentacoes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('insumo_id', UUID(as_uuid=True), sa.ForeignKey('insumos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('quantidade', sa.Integer, nullable=False),
        sa.Column('tipo_movimento', sa.String(10), nullable=False),
        sa.Column('motivo', sa.String(255), nullable=True),
        sa.Column('estoque_anterior', sa.Integer, nullable=False),
        sa.Column('estoque_resultante', sa.Integer, nullable=False),
        sa.Column('observacao', sa.String, nullable=True),
        sa.Column('usuario_id', UUID(as_uuid=True), nullable=True),
        sa.Column('subscriber_id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Index('ix_insumo_movimentacoes_insumo_id', 'insumo_id'),
        sa.Index('ix_insumo_movimentacoes_subscriber_id', 'subscriber_id'),
        sa.Index('ix_insumo_movimentacoes_created_at', 'created_at')
    )


def downgrade() -> None:
    # Remove a tabela ao fazer downgrade
    op.drop_table('insumo_movimentacoes')