"""
Modelos SQLAlchemy para o domínio de Insumos.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class InsumoMovimentacao(Base):
    """
    Modelo para o histórico de movimentações de estoque de insumos.
    
    Registra todas as entradas e saídas de estoque, com informações
    de rastreabilidade como usuário responsável, motivo, quantidade e timestamps.
    """
    __tablename__ = "insumo_movimentacoes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    insumo_id = Column(UUID(as_uuid=True), ForeignKey("insumos.id", ondelete="CASCADE"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    tipo_movimento = Column(String(10), nullable=False)  # 'entrada' ou 'saida'
    motivo = Column(String(255), nullable=True)
    estoque_anterior = Column(Integer, nullable=False)
    estoque_resultante = Column(Integer, nullable=False)
    observacao = Column(String, nullable=True)
    usuario_id = Column(UUID(as_uuid=True), nullable=True)
    subscriber_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Índices para otimização
    __table_args__ = (
        Index('ix_insumo_movimentacoes_insumo_id', 'insumo_id'),
        Index('ix_insumo_movimentacoes_created_at', 'created_at'),
    )
    
    # Relacionamentos
    insumo = relationship("Insumo", back_populates="movimentacoes")
    
    def __init__(
        self,
        insumo_id: UUID,
        quantidade: int,
        tipo_movimento: str,
        estoque_anterior: int,
        estoque_resultante: int,
        subscriber_id: UUID,
        motivo: Optional[str] = None,
        observacao: Optional[str] = None,
        usuario_id: Optional[UUID] = None,
        id = None,
        created_at = None
    ):
        """
        Inicializa um novo registro de movimentação de estoque.
        
        Args:
            insumo_id: ID do insumo movimentado
            quantidade: Quantidade movimentada (sempre positiva)
            tipo_movimento: 'entrada' ou 'saida'
            estoque_anterior: Estoque antes da movimentação
            estoque_resultante: Estoque após a movimentação
            subscriber_id: ID do assinante (isolamento multitenant)
            motivo: Motivo da movimentação (opcional)
            observacao: Detalhes adicionais (opcional)
            usuario_id: ID do usuário responsável (opcional)
            id: UUID da movimentação, gerado automaticamente se não fornecido
            created_at: Data de criação do registro
        """
        self.id = id if id else uuid4()
        self.insumo_id = insumo_id
        self.quantidade = quantidade
        self.tipo_movimento = tipo_movimento
        self.motivo = motivo
        self.estoque_anterior = estoque_anterior
        self.estoque_resultante = estoque_resultante
        self.observacao = observacao
        self.usuario_id = usuario_id
        self.subscriber_id = subscriber_id
        self.created_at = created_at if created_at else datetime.utcnow()


class InsumoModuleAssociation(Base):
    """
    Modelo para a associação entre Insumos e Módulos.
    
    Esta é uma tabela de relacionamento N:M entre Insumos e Módulos,
    que armazena detalhes específicos da associação.
    """
    __tablename__ = "insumos_modules_association"
    
    insumo_id = Column(UUID(as_uuid=True), ForeignKey("insumos.id", ondelete="CASCADE"), primary_key=True)
    module_id = Column(UUID(as_uuid=True), primary_key=True)
    quantidade_padrao = Column(Integer, default=1, nullable=False)
    observacao = Column(String, nullable=True)
    
    insumo = relationship("Insumo", back_populates="modules_used")
    
    def __init__(
        self,
        insumo_id: UUID,
        module_id: UUID,
        quantidade_padrao: int = 1,
        observacao: Optional[str] = None
    ):
        """
        Inicializa uma nova associação entre Insumo e Módulo.
        
        Args:
            insumo_id: ID do insumo associado
            module_id: ID do módulo associado
            quantidade_padrao: Quantidade padrão do insumo utilizada no módulo
            observacao: Observação sobre a utilização (opcional)
        """
        self.insumo_id = insumo_id
        self.module_id = module_id
        self.quantidade_padrao = quantidade_padrao
        self.observacao = observacao


class Insumo(Base):
    """
    Modelo de banco de dados para Insumos (suprimentos).
    
    Armazena dados de insumos utilizados nos serviços,
    com detalhes como estoque, valor, categorias e associações.
    """
    __tablename__ = "insumos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    valor_unitario = Column(Float, nullable=False)
    unidade_medida = Column(String, nullable=False)
    estoque_minimo = Column(Integer, nullable=False, default=0)
    estoque_atual = Column(Integer, nullable=False, default=0)
    subscriber_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    fornecedor = Column(String, nullable=True)
    codigo_referencia = Column(String, nullable=True)
    data_validade = Column(DateTime, nullable=True)
    data_compra = Column(DateTime, nullable=True)
    observacoes = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relacionamentos
    modules_used = relationship(
        "InsumoModuleAssociation",
        back_populates="insumo",
        cascade="all, delete-orphan"
    )
    
    # Relacionamento com o histórico de movimentações
    movimentacoes = relationship(
        "InsumoMovimentacao",
        back_populates="insumo",
        cascade="all, delete-orphan"
    )
    
    def __init__(
        self,
        nome: str,
        descricao: str,
        categoria: str,
        valor_unitario: float,
        unidade_medida: str,
        estoque_minimo: int,
        estoque_atual: int,
        subscriber_id,
        fornecedor: str = None,
        codigo_referencia: str = None,
        data_validade = None,
        data_compra = None,
        observacoes: str = None,
        id = None,
        is_active: bool = True,
        created_at = None,
        updated_at = None
    ):
        """
        Inicializa um novo Insumo.
        
        Args:
            nome: Nome do insumo
            descricao: Descrição detalhada
            categoria: Categoria do insumo (ex: "medicamento", "material")
            valor_unitario: Valor unitário do insumo
            unidade_medida: Unidade de medida (ex: "unidade", "ml", "caixa")
            estoque_minimo: Estoque mínimo recomendado
            estoque_atual: Quantidade atual em estoque
            subscriber_id: ID do assinante (isolamento multitenant)
            fornecedor: Nome do fornecedor (opcional)
            codigo_referencia: Código de referência (opcional)
            data_validade: Data de validade (opcional)
            data_compra: Data da última compra (opcional)
            observacoes: Observações adicionais (opcional)
            id: UUID do insumo, gerado automaticamente se não fornecido
            is_active: Indica se o insumo está ativo
            created_at: Data de criação
            updated_at: Data da última atualização
        """
        self.id = id if id else uuid4()
        self.nome = nome
        self.descricao = descricao
        self.categoria = categoria
        self.valor_unitario = valor_unitario
        self.unidade_medida = unidade_medida
        self.estoque_minimo = estoque_minimo
        self.estoque_atual = estoque_atual
        self.subscriber_id = subscriber_id
        self.fornecedor = fornecedor
        self.codigo_referencia = codigo_referencia
        self.data_validade = data_validade
        self.data_compra = data_compra
        self.observacoes = observacoes
        self.is_active = is_active
        self.created_at = created_at if created_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()