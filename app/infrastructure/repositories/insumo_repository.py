"""
Implementação do repositório de insumos usando SQLAlchemy.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from app.db.models import Insumo, Module
from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface
from app.infrastructure.adapters.insumo_adapter import InsumoAdapter


class SQLAlchemyInsumoRepository(InsumoRepositoryInterface):
    """
    Implementação do repositório de insumos usando SQLAlchemy.
    
    Esta classe implementa a interface InsumoRepositoryInterface usando
    SQLAlchemy como ORM para acessar o banco de dados PostgreSQL.
    """
    
    def __init__(self, session: Session):
        """
        Inicializa o repositório com uma sessão SQLAlchemy.
        
        Args:
            session: Sessão SQLAlchemy para acesso ao banco de dados
        """
        self.session = session
    
    def create(self, 
               nome: str,
               descricao: str,
               categoria: str,
               valor_unitario: float,
               unidade_medida: str,
               estoque_minimo: int,
               estoque_atual: int,
               subscriber_id: UUID,
               fornecedor: Optional[str] = None,
               codigo_referencia: Optional[str] = None,
               data_validade: Optional[str] = None,
               data_compra: Optional[str] = None,
               observacoes: Optional[str] = None,
               modules_used: Optional[List[Dict[str, Any]]] = None) -> InsumoEntity:
        """
        Cria um novo insumo no banco de dados.
        
        Args:
            nome: Nome do insumo
            descricao: Descrição detalhada
            categoria: Categoria do insumo
            valor_unitario: Valor unitário
            unidade_medida: Unidade de medida
            estoque_minimo: Estoque mínimo recomendado
            estoque_atual: Estoque atual
            subscriber_id: ID do assinante proprietário
            fornecedor: Nome do fornecedor (opcional)
            codigo_referencia: Código de referência (opcional)
            data_validade: Data de validade (opcional)
            data_compra: Data de compra (opcional)
            observacoes: Observações adicionais (opcional)
            modules_used: Lista de módulos que usam este insumo (opcional)
            
        Returns:
            InsumoEntity: Entidade de insumo criada
        """
        # Criar modelo de insumo
        insumo = Insumo(
            nome=nome,
            descricao=descricao,
            categoria=categoria,
            valor_unitario=valor_unitario,
            unidade_medida=unidade_medida,
            estoque_minimo=estoque_minimo,
            estoque_atual=estoque_atual,
            subscriber_id=subscriber_id,
            fornecedor=fornecedor,
            codigo_referencia=codigo_referencia,
            data_validade=data_validade,
            data_compra=data_compra,
            observacoes=observacoes
        )
        
        # Adicionar à sessão
        self.session.add(insumo)
        self.session.flush()  # Para obter o ID gerado
        
        # Adicionar associações com módulos, se houver
        if modules_used:
            associations = InsumoAdapter.map_module_associations(
                insumo_id=insumo.id,
                modules_data=modules_used,
                session=self.session
            )
            
            for association in associations:
                self.session.add(association)
            
            self.session.flush()
        
        # Commit das alterações
        self.session.commit()
        
        # Converter para entidade de domínio e retornar
        return InsumoAdapter.to_entity(insumo)
    
    def get_by_id(self, insumo_id: UUID) -> Optional[InsumoEntity]:
        """
        Obtém um insumo pelo ID.
        
        Args:
            insumo_id: UUID do insumo
            
        Returns:
            Optional[InsumoEntity]: Entidade de insumo ou None se não encontrado
        """
        insumo = self.session.query(Insumo).filter(
            Insumo.id == insumo_id,
            Insumo.is_active == True
        ).first()
        
        if not insumo:
            return None
        
        return InsumoAdapter.to_entity(insumo)
    
    def list(self, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Lista insumos com paginação e filtros.
        
        Args:
            skip: Quantos insumos pular (paginação)
            limit: Limite de insumos a retornar
            filters: Filtros a aplicar
            
        Returns:
            Dict[str, Any]: Dicionário com itens, total, skip e limit
        """
        # Inicializar query
        query = self.session.query(Insumo).filter(Insumo.is_active == True)
        
        # Aplicar filtros se houver
        if filters:
            query = self._apply_filters(query, filters)
        
        # Contar total antes da paginação
        total = query.count()
        
        # Aplicar paginação
        insumos = query.order_by(Insumo.nome).offset(skip).limit(limit).all()
        
        # Converter para entidades de domínio
        insumo_entities = [InsumoAdapter.to_entity(insumo) for insumo in insumos]
        
        # Retornar resultado paginado
        return {
            "items": insumo_entities,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    def list_by_subscriber(self, subscriber_id: UUID, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Lista insumos de um assinante específico.
        
        Args:
            subscriber_id: ID do assinante
            skip: Quantos insumos pular (paginação)
            limit: Limite de insumos a retornar
            filters: Filtros a aplicar
            
        Returns:
            Dict[str, Any]: Dicionário com itens, total, skip e limit
        """
        # Inicializar query com filtro de assinante
        query = self.session.query(Insumo).filter(
            Insumo.subscriber_id == subscriber_id,
            Insumo.is_active == True
        )
        
        # Aplicar filtros adicionais se houver
        if filters:
            query = self._apply_filters(query, filters)
        
        # Contar total antes da paginação
        total = query.count()
        
        # Aplicar paginação
        insumos = query.order_by(Insumo.nome).offset(skip).limit(limit).all()
        
        # Converter para entidades de domínio
        insumo_entities = [InsumoAdapter.to_entity(insumo) for insumo in insumos]
        
        # Retornar resultado paginado
        return {
            "items": insumo_entities,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    def update(self, insumo_id: UUID, data: Dict[str, Any]) -> Optional[InsumoEntity]:
        """
        Atualiza um insumo existente.
        
        Args:
            insumo_id: UUID do insumo a atualizar
            data: Dicionário com campos a atualizar
            
        Returns:
            Optional[InsumoEntity]: Entidade atualizada ou None se não encontrado
        """
        # Buscar insumo no banco de dados
        insumo = self.session.query(Insumo).filter(
            Insumo.id == insumo_id,
            Insumo.is_active == True
        ).first()
        
        if not insumo:
            return None
        
        # Atualizar campos do insumo
        for key, value in data.items():
            if hasattr(insumo, key) and key != 'id' and key != 'subscriber_id' and key != 'modules_used':
                setattr(insumo, key, value)
        
        # Atualizar associações com módulos, se fornecido
        if 'modules_used' in data and data['modules_used'] is not None:
            # Remover associações atuais
            for association in insumo.modules_used:
                self.session.delete(association)
            
            # Adicionar novas associações
            associations = InsumoAdapter.map_module_associations(
                insumo_id=insumo.id,
                modules_data=data['modules_used'],
                session=self.session
            )
            
            for association in associations:
                self.session.add(association)
        
        # Atualizar timestamp
        insumo.updated_at = datetime.utcnow()
        
        # Persistir alterações
        self.session.commit()
        
        # Retornar entidade atualizada
        return InsumoAdapter.to_entity(insumo)
    
    def delete(self, insumo_id: UUID) -> bool:
        """
        Exclui logicamente um insumo (soft delete).
        
        Args:
            insumo_id: UUID do insumo a excluir
            
        Returns:
            bool: True se bem-sucedido, False caso contrário
        """
        # Buscar insumo no banco de dados
        insumo = self.session.query(Insumo).filter(
            Insumo.id == insumo_id,
            Insumo.is_active == True
        ).first()
        
        if not insumo:
            return False
        
        # Marcar como inativo (soft delete)
        insumo.is_active = False
        insumo.updated_at = datetime.utcnow()
        
        # Persistir alterações
        self.session.commit()
        
        return True
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """
        Aplica filtros à query SQLAlchemy.
        
        Args:
            query: Query SQLAlchemy base
            filters: Dicionário de filtros a aplicar
            
        Returns:
            Query atualizada com filtros
        """
        if 'nome' in filters and filters['nome']:
            query = query.filter(Insumo.nome.ilike(f"%{filters['nome']}%"))
        
        if 'categoria' in filters and filters['categoria']:
            query = query.filter(Insumo.categoria == filters['categoria'])
        
        if 'fornecedor' in filters and filters['fornecedor']:
            query = query.filter(Insumo.fornecedor.ilike(f"%{filters['fornecedor']}%"))
        
        if 'estoque_baixo' in filters and filters['estoque_baixo']:
            query = query.filter(Insumo.estoque_atual < Insumo.estoque_minimo)
        
        if 'module_id' in filters and filters['module_id']:
            query = query.join(Insumo.modules_used).filter(
                Insumo.modules_used.any(module_id=filters['module_id'])
            )
        
        return query