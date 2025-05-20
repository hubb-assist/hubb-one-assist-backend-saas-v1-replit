"""
Implementação do repositório de Insumos.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.domain.insumo.interfaces import InsumoRepositoryInterface
from app.domain.insumo.entities import InsumoEntity
from app.infrastructure.adapters.insumo_adapter import InsumoAdapter
from app.db.models.insumo import Insumo
from app.core.exceptions import EntityNotFoundException


class InsumoRepositoryImpl(InsumoRepositoryInterface):
    """
    Implementação do repositório de Insumos.
    """
    
    def __init__(self, db: Session):
        """
        Inicializa o repositório.
        
        Args:
            db: Sessão do banco de dados
        """
        self.db = db
        self.adapter = InsumoAdapter()
    
    def create(self, entity: InsumoEntity) -> InsumoEntity:
        """
        Cria um novo insumo no repositório.
        
        Args:
            entity: Entidade de Insumo a ser criada
            
        Returns:
            InsumoEntity: Entidade criada com ID
        """
        # Converter entidade para modelo ORM
        orm_model = self.adapter.to_orm_model(entity)
        
        # Persistir no banco de dados
        self.db.add(orm_model)
        self.db.commit()
        self.db.refresh(orm_model)
        
        # Converter de volta para entidade
        return self.adapter.to_entity(orm_model)
    
    def get_by_id(self, insumo_id: UUID, subscriber_id: UUID) -> InsumoEntity:
        """
        Obtém um insumo pelo ID.
        
        Args:
            insumo_id: ID do insumo a ser obtido
            subscriber_id: ID do assinante proprietário
            
        Returns:
            InsumoEntity: Entidade de Insumo encontrada
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado
        """
        # Buscar no banco de dados
        orm_model = self.db.query(Insumo).filter(
            Insumo.id == insumo_id,
            Insumo.subscriber_id == subscriber_id,
            Insumo.is_active == True
        ).first()
        
        # Verificar se encontrou
        if not orm_model:
            raise EntityNotFoundException(f"Insumo com ID {insumo_id} não encontrado")
        
        # Converter para entidade
        entity = self.adapter.to_entity(orm_model)
        
        return entity
    
    def update(self, entity: InsumoEntity) -> InsumoEntity:
        """
        Atualiza um insumo existente.
        
        Args:
            entity: Entidade de Insumo com os dados atualizados
            
        Returns:
            InsumoEntity: Entidade atualizada
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado
        """
        # Buscar no banco de dados
        orm_model = self.db.query(Insumo).filter(
            Insumo.id == entity.id,
            Insumo.subscriber_id == entity.subscriber_id,
            Insumo.is_active == True
        ).first()
        
        # Verificar se encontrou
        if not orm_model:
            raise EntityNotFoundException(f"Insumo com ID {entity.id} não encontrado")
        
        # Atualizar campos
        orm_model = self.adapter.update_orm_model(orm_model, entity)
        
        # Persistir no banco de dados
        self.db.commit()
        self.db.refresh(orm_model)
        
        # Converter para entidade
        return self.adapter.to_entity(orm_model)
    
    def delete(self, insumo_id: UUID, subscriber_id: UUID) -> None:
        """
        Exclui logicamente um insumo (soft delete).
        
        Args:
            insumo_id: ID do insumo a ser excluído
            subscriber_id: ID do assinante proprietário
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado
        """
        # Buscar no banco de dados
        orm_model = self.db.query(Insumo).filter(
            Insumo.id == insumo_id,
            Insumo.subscriber_id == subscriber_id,
            Insumo.is_active == True
        ).first()
        
        # Verificar se encontrou
        if not orm_model:
            raise EntityNotFoundException(f"Insumo com ID {insumo_id} não encontrado")
        
        # Desativar (exclusão lógica)
        orm_model.is_active = False
        
        # Persistir no banco de dados
        self.db.commit()
    
    def list(self, 
            subscriber_id: UUID,
            skip: int = 0,
            limit: int = 100,
            filters: Optional[Dict[str, Any]] = None,
            ) -> List[InsumoEntity]:
        """
        Lista insumos com paginação e filtros opcionais.
        
        Args:
            subscriber_id: ID do assinante proprietário
            skip: Número de registros a pular (para paginação)
            limit: Número máximo de registros a retornar
            filters: Filtros opcionais a serem aplicados
            
        Returns:
            List[InsumoEntity]: Lista de entidades de Insumo
        """
        # Iniciar consulta
        query = self.db.query(Insumo).filter(
            Insumo.subscriber_id == subscriber_id
        )
        
        # Aplicar filtros se fornecidos
        if filters:
            # Filtro por nome (parcial)
            if "nome" in filters:
                query = query.filter(Insumo.nome.ilike(f"%{filters['nome']}%"))
            
            # Filtro por tipo
            if "tipo" in filters:
                query = query.filter(Insumo.tipo == filters["tipo"])
            
            # Filtro por categoria
            if "categoria" in filters:
                query = query.filter(Insumo.categoria == filters["categoria"])
            
            # Filtro por módulo
            if "modulo_id" in filters:
                query = query.filter(Insumo.modulo_id == filters["modulo_id"])
            
            # Filtro por status de ativação
            if "is_active" in filters:
                query = query.filter(Insumo.is_active == filters["is_active"])
        else:
            # Por padrão, mostrar apenas os ativos
            query = query.filter(Insumo.is_active == True)
        
        # Aplicar paginação
        query = query.offset(skip).limit(limit)
        
        # Executar a consulta
        orm_models = query.all()
        
        # Converter para entidades
        entities = [self.adapter.to_entity(orm_model) for orm_model in orm_models]
        
        return entities