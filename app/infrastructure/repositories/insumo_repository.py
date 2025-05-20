"""
Implementação do repositório de insumos utilizando SQLAlchemy.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundException
from app.db.models.insumo import Insumo
from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface
from app.infrastructure.adapters.insumo_adapter import InsumoAdapter


class InsumoRepository(InsumoRepositoryInterface):
    """
    Implementação do repositório de insumos utilizando SQLAlchemy.
    """
    
    def __init__(self, db: Session):
        """
        Inicializa o repositório com a sessão do banco de dados.
        
        Args:
            db: Sessão do banco de dados SQLAlchemy
        """
        self.db = db
    
    def create(self, entity: InsumoEntity) -> InsumoEntity:
        """
        Cria um novo insumo no banco de dados.
        
        Args:
            entity: Entidade de insumo a ser criada
            
        Returns:
            InsumoEntity: Entidade de insumo criada com ID gerado
            
        Raises:
            ValueError: Se houver validação inválida
        """
        try:
            # Converter entidade para modelo
            model = InsumoAdapter.to_model(entity)
            
            # Persistir no banco de dados
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            
            # Converter de volta para entidade
            return InsumoAdapter.to_entity(model)
            
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Erro ao criar insumo: {str(e)}")
    
    def get_by_id(self, insumo_id: UUID, subscriber_id: UUID) -> InsumoEntity:
        """
        Obtém um insumo pelo ID.
        
        Args:
            insumo_id: ID do insumo a ser obtido
            subscriber_id: ID do assinante proprietário para validação
            
        Returns:
            InsumoEntity: Entidade de insumo encontrada
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado
        """
        # Buscar insumo no banco de dados
        model = self.db.query(Insumo).filter(
            Insumo.id == insumo_id,
            Insumo.subscriber_id == subscriber_id,
            Insumo.is_active == True
        ).first()
        
        # Verificar se encontrou o insumo
        if not model:
            raise EntityNotFoundException(f"Insumo com ID {insumo_id} não encontrado")
        
        # Converter para entidade
        return InsumoAdapter.to_entity(model)
    
    def update(self, insumo_id: UUID, subscriber_id: UUID, update_data: dict) -> InsumoEntity:
        """
        Atualiza um insumo existente.
        
        Args:
            insumo_id: ID do insumo a ser atualizado
            subscriber_id: ID do assinante proprietário para validação
            update_data: Dados a serem atualizados no insumo
            
        Returns:
            InsumoEntity: Entidade de insumo atualizada
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado
            ValueError: Se houver validação inválida
        """
        try:
            # Verificar se o insumo existe
            model = self.db.query(Insumo).filter(
                Insumo.id == insumo_id,
                Insumo.subscriber_id == subscriber_id,
                Insumo.is_active == True
            ).first()
            
            if not model:
                raise EntityNotFoundException(f"Insumo com ID {insumo_id} não encontrado")
            
            # Atualizar campos do modelo a partir do dicionário update_data
            if "nome" in update_data:
                setattr(model, "nome", update_data["nome"])
            if "tipo" in update_data:
                setattr(model, "tipo", update_data["tipo"])
            if "unidade" in update_data:
                setattr(model, "unidade", update_data["unidade"])
            if "quantidade" in update_data:
                setattr(model, "quantidade", update_data["quantidade"])
            if "categoria" in update_data:
                setattr(model, "categoria", update_data["categoria"])
            if "modulo_id" in update_data:
                setattr(model, "modulo_id", update_data["modulo_id"])
            if "observacoes" in update_data:
                setattr(model, "observacoes", update_data["observacoes"])
            if "is_active" in update_data:
                setattr(model, "is_active", update_data["is_active"])
                
            # Atualizar timestamp
            setattr(model, "updated_at", datetime.utcnow())
            
            # Persistir alterações
            self.db.commit()
            self.db.refresh(model)
            
            # Converter para entidade
            return InsumoAdapter.to_entity(model)
            
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Erro ao atualizar insumo: {str(e)}")
    
    def delete(self, insumo_id: UUID, subscriber_id: UUID) -> None:
        """
        Exclui logicamente um insumo (marca como inativo).
        
        Args:
            insumo_id: ID do insumo a ser excluído
            subscriber_id: ID do assinante proprietário para validação
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado
        """
        # Verificar se o insumo existe
        model = self.db.query(Insumo).filter(
            Insumo.id == insumo_id,
            Insumo.subscriber_id == subscriber_id,
            Insumo.is_active == True
        ).first()
        
        if not model:
            raise EntityNotFoundException(f"Insumo com ID {insumo_id} não encontrado")
        
        # Marcar como inativo (exclusão lógica)
        setattr(model, "is_active", False)
        setattr(model, "updated_at", datetime.utcnow())
        
        # Persistir alterações
        self.db.commit()
    
    def list_by_subscriber(
        self, 
        subscriber_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        categoria: Optional[str] = None,
        tipo: Optional[str] = None,
        modulo_id: Optional[UUID] = None,
        is_active: bool = True
    ) -> List[InsumoEntity]:
        """
        Lista insumos de um assinante com filtros opcionais.
        
        Args:
            subscriber_id: ID do assinante proprietário
            skip: Quantidade de registros para pular (para paginação)
            limit: Limite de registros retornados (para paginação)
            categoria: Filtro opcional por categoria
            tipo: Filtro opcional por tipo
            modulo_id: Filtro opcional por módulo
            is_active: Filtro por status de ativação (padrão: True)
            
        Returns:
            List[InsumoEntity]: Lista de entidades de insumo
        """
        # Iniciar query
        query = self.db.query(Insumo).filter(
            Insumo.subscriber_id == subscriber_id,
            Insumo.is_active == is_active
        )
        
        # Aplicar filtros adicionais, se fornecidos
        if categoria:
            query = query.filter(Insumo.categoria == categoria)
        
        if tipo:
            query = query.filter(Insumo.tipo == tipo)
        
        if modulo_id:
            query = query.filter(Insumo.modulo_id == modulo_id)
        
        # Executar consulta com paginação
        models = query.order_by(Insumo.nome).offset(skip).limit(limit).all()
        
        # Converter para entidades
        return InsumoAdapter.to_entity_list(models)