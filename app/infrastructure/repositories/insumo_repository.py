"""
Implementação SQLAlchemy do repositório de Insumos.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.domain.insumo.interfaces import InsumoRepository
from app.domain.insumo.entities import InsumoEntity
from app.schemas.insumo import InsumoCreate, InsumoUpdate
from app.infrastructure.adapters.insumo_adapter import InsumoAdapter
from app.db.models.insumo import Insumo, insumo_modulo


class InsumoSQLAlchemyRepository(InsumoRepository):
    """
    Implementação do repositório de Insumos utilizando SQLAlchemy.
    """
    
    def __init__(self, db: Session):
        """
        Inicializa o repositório com uma sessão de banco de dados.
        
        Args:
            db: Sessão de banco de dados SQLAlchemy
        """
        self.db = db
    
    def create(self, insumo_data: InsumoCreate, subscriber_id: UUID) -> InsumoEntity:
        """
        Cria um novo insumo.
        
        Args:
            insumo_data: Dados do insumo a ser criado
            subscriber_id: ID do assinante para associação (multitenancy)
            
        Returns:
            InsumoEntity: Entidade de insumo criada
        """
        # Criar entidade de domínio
        entity = InsumoEntity(
            subscriber_id=subscriber_id,
            nome=insumo_data.nome,
            tipo=insumo_data.tipo,
            unidade=insumo_data.unidade,
            valor=insumo_data.valor,
            observacoes=insumo_data.observacoes,
            categoria=insumo_data.categoria,
            modulos=insumo_data.modulos
        )
        
        # Converter para modelo ORM e persistir
        orm_model = InsumoAdapter.to_orm_model(entity, self.db)
        self.db.add(orm_model)
        self.db.commit()
        self.db.refresh(orm_model)
        
        # Retornar entidade atualizada
        return InsumoAdapter.to_entity(orm_model)
    
    def get_by_id(self, insumo_id: UUID, subscriber_id: UUID) -> Optional[InsumoEntity]:
        """
        Busca um insumo pelo seu ID.
        
        Args:
            insumo_id: ID do insumo a ser buscado
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            Optional[InsumoEntity]: Entidade de insumo se encontrada, None caso contrário
        """
        orm_model = self.db.query(Insumo).filter(
            Insumo.id == insumo_id,
            Insumo.subscriber_id == subscriber_id,
            Insumo.is_active == True
        ).first()
        
        return InsumoAdapter.to_entity(orm_model)
    
    def update(self, insumo_id: UUID, insumo_data: InsumoUpdate, subscriber_id: UUID) -> Optional[InsumoEntity]:
        """
        Atualiza um insumo existente.
        
        Args:
            insumo_id: ID do insumo a ser atualizado
            insumo_data: Dados a serem atualizados
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            Optional[InsumoEntity]: Entidade de insumo atualizada, None se não encontrada
        """
        # Buscar o insumo atual
        orm_model = self.db.query(Insumo).filter(
            Insumo.id == insumo_id,
            Insumo.subscriber_id == subscriber_id,
            Insumo.is_active == True
        ).first()
        
        if not orm_model:
            return None
        
        # Converter para entidade e atualizar com novos dados
        entity = InsumoAdapter.to_entity(orm_model)
        
        # Atualizar apenas os campos fornecidos
        entity.update_info(
            nome=insumo_data.nome,
            tipo=insumo_data.tipo,
            unidade=insumo_data.unidade,
            valor=insumo_data.valor,
            observacoes=insumo_data.observacoes,
            categoria=insumo_data.categoria,
            modulos=insumo_data.modulos
        )
        
        # Atualizar o modelo ORM
        orm_model = InsumoAdapter.to_orm_model(entity, self.db, orm_model)
        self.db.commit()
        self.db.refresh(orm_model)
        
        return InsumoAdapter.to_entity(orm_model)
    
    def delete(self, insumo_id: UUID, subscriber_id: UUID) -> bool:
        """
        Desativa um insumo logicamente.
        
        Args:
            insumo_id: ID do insumo a ser desativado
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            bool: True se desativado com sucesso, False caso contrário
        """
        orm_model = self.db.query(Insumo).filter(
            Insumo.id == insumo_id,
            Insumo.subscriber_id == subscriber_id,
            Insumo.is_active == True
        ).first()
        
        if not orm_model:
            return False
        
        # Converter para entidade e desativar
        entity = InsumoAdapter.to_entity(orm_model)
        entity.deactivate()
        
        # Atualizar o modelo ORM
        orm_model = InsumoAdapter.to_orm_model(entity, self.db, orm_model)
        self.db.commit()
        
        return True
    
    def list_all(
        self,
        subscriber_id: UUID,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[InsumoEntity]:
        """
        Lista todos os insumos com paginação e filtros opcionais.
        
        Args:
            subscriber_id: ID do assinante (isolamento multitenancy)
            skip: Quantidade de registros para pular
            limit: Limite de registros a retornar
            filters: Filtros adicionais como categoria ou módulos
            
        Returns:
            List[InsumoEntity]: Lista de entidades de insumo
        """
        filters = filters or {}
        query = self.db.query(Insumo).filter(
            Insumo.subscriber_id == subscriber_id,
            Insumo.is_active == True
        )
        
        # Aplicar filtros
        if 'categoria' in filters and filters['categoria']:
            query = query.filter(Insumo.categoria == filters['categoria'])
        
        if 'modulos' in filters and filters['modulos']:
            modulos = filters['modulos']
            if isinstance(modulos, list) and modulos:
                # Filtrar por insumos que pertencem a qualquer um dos módulos especificados
                query = query.join(insumo_modulo).filter(
                    insumo_modulo.c.modulo.in_(modulos)
                )
        
        if 'nome' in filters and filters['nome']:
            query = query.filter(Insumo.nome.ilike(f"%{filters['nome']}%"))
        
        if 'tipo' in filters and filters['tipo']:
            query = query.filter(Insumo.tipo == filters['tipo'])
        
        # Aplicar paginação
        query = query.order_by(Insumo.nome).offset(skip).limit(limit)
        
        # Converter para entidades e retornar
        orm_models = query.all()
        return [InsumoAdapter.to_entity(m) for m in orm_models]
    
    def count(self, subscriber_id: UUID, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Conta o número total de insumos com base nos filtros.
        
        Args:
            subscriber_id: ID do assinante (isolamento multitenancy)
            filters: Filtros adicionais como categoria ou módulos
            
        Returns:
            int: Número total de insumos
        """
        filters = filters or {}
        query = self.db.query(Insumo).filter(
            Insumo.subscriber_id == subscriber_id,
            Insumo.is_active == True
        )
        
        # Aplicar filtros
        if 'categoria' in filters and filters['categoria']:
            query = query.filter(Insumo.categoria == filters['categoria'])
        
        if 'modulos' in filters and filters['modulos']:
            modulos = filters['modulos']
            if isinstance(modulos, list) and modulos:
                query = query.join(insumo_modulo).filter(
                    insumo_modulo.c.modulo.in_(modulos)
                )
        
        if 'nome' in filters and filters['nome']:
            query = query.filter(Insumo.nome.ilike(f"%{filters['nome']}%"))
        
        if 'tipo' in filters and filters['tipo']:
            query = query.filter(Insumo.tipo == filters['tipo'])
        
        return query.count()