"""
Implementação do repositório de Insumos usando SQLAlchemy.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.db.models.insumo import Insumo, InsumoModuleAssociation
from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface
from app.infrastructure.adapters.insumo_adapter import InsumoAdapter


class SQLAlchemyInsumoRepository(InsumoRepositoryInterface):
    """
    Implementação do repositório de Insumos usando SQLAlchemy.
    
    Esta classe concreta implementa os métodos definidos na interface
    do repositório, fornecendo acesso aos dados usando SQLAlchemy.
    """
    
    def __init__(self, db_session: Session):
        """
        Inicializa o repositório com uma sessão de banco de dados.
        
        Args:
            db_session: Sessão SQLAlchemy para operações no banco
        """
        self.db_session = db_session
    
    def create(self, entity: InsumoEntity) -> InsumoEntity:
        """
        Cria um novo insumo no banco de dados.
        
        Args:
            entity: Entidade de insumo a ser criada
            
        Returns:
            InsumoEntity: Entidade criada, com ID atribuído
            
        Raises:
            ValueError: Se ocorrer um erro ao criar o insumo
        """
        try:
            # Converter entidade em modelo
            model = InsumoAdapter.to_model(entity)
            
            # Persistir no banco
            self.db_session.add(model)
            self.db_session.flush()  # Obter ID gerado
            
            # Criar associações com módulos, se houver
            if entity.modules_used:
                for module_assoc in entity.modules_used:
                    assoc_model = InsumoModuleAssociation(
                        insumo_id=model.id,
                        module_id=module_assoc.module_id,
                        quantidade_padrao=module_assoc.quantidade_padrao,
                        observacao=module_assoc.observacao
                    )
                    self.db_session.add(assoc_model)
                
                self.db_session.flush()
            
            # Commit
            self.db_session.commit()
            
            # Converter de volta para entidade e retornar
            return InsumoAdapter.to_entity(model)
            
        except IntegrityError as e:
            self.db_session.rollback()
            raise ValueError(f"Erro de integridade ao criar insumo: {str(e)}")
        except Exception as e:
            self.db_session.rollback()
            raise ValueError(f"Erro ao criar insumo: {str(e)}")
    
    def get_by_id(self, insumo_id: UUID) -> Optional[InsumoEntity]:
        """
        Busca um insumo pelo ID.
        
        Args:
            insumo_id: ID do insumo a ser buscado
            
        Returns:
            Optional[InsumoEntity]: Entidade encontrada ou None se não existir
        """
        try:
            # Buscar insumo com associações
            insumo = (
                self.db_session.query(Insumo)
                .options(joinedload(Insumo.modules_used))
                .filter(Insumo.id == insumo_id, Insumo.is_active == True)
                .first()
            )
            
            if not insumo:
                return None
                
            # Converter para entidade e retornar
            return InsumoAdapter.to_entity(insumo)
            
        except Exception as e:
            raise ValueError(f"Erro ao buscar insumo: {str(e)}")
    
    def list(self, subscriber_id: UUID, filters: Dict[str, Any] = None) -> List[InsumoEntity]:
        """
        Lista insumos com filtros opcionais.
        
        Args:
            subscriber_id: ID do assinante para filtrar insumos
            filters: Dicionário de filtros a serem aplicados
            
        Returns:
            List[InsumoEntity]: Lista de entidades de insumo
        """
        try:
            # Iniciar query
            query = (
                self.db_session.query(Insumo)
                .options(joinedload(Insumo.modules_used))
                .filter(Insumo.subscriber_id == subscriber_id, Insumo.is_active == True)
            )
            
            # Aplicar filtros adicionais
            if filters:
                query = InsumoAdapter.apply_filters(query, filters)
            
            # Executar consulta
            insumos = query.all()
            
            # Converter para entidades
            return [InsumoAdapter.to_entity(insumo) for insumo in insumos]
            
        except Exception as e:
            raise ValueError(f"Erro ao listar insumos: {str(e)}")
    
    def update(self, entity: InsumoEntity) -> InsumoEntity:
        """
        Atualiza um insumo existente.
        
        Args:
            entity: Entidade de insumo com dados atualizados
            
        Returns:
            InsumoEntity: Entidade atualizada
            
        Raises:
            ValueError: Se o insumo não existir
        """
        try:
            # Buscar insumo existente
            insumo = (
                self.db_session.query(Insumo)
                .options(joinedload(Insumo.modules_used))
                .filter(Insumo.id == entity.id, Insumo.is_active == True)
                .first()
            )
            
            if not insumo:
                raise ValueError(f"Insumo com ID {entity.id} não encontrado")
            
            # Validar pertencimento ao subscriber
            if insumo.subscriber_id != entity.subscriber_id:
                raise ValueError(f"Insumo não pertence ao subscriber informado")
            
            # Atualizar modelo com dados da entidade
            InsumoAdapter.update_model_from_entity(insumo, entity, update_modules=True)
            
            # Commit
            self.db_session.commit()
            
            # Retornar entidade atualizada
            return InsumoAdapter.to_entity(insumo)
            
        except IntegrityError as e:
            self.db_session.rollback()
            raise ValueError(f"Erro de integridade ao atualizar insumo: {str(e)}")
        except ValueError as e:
            self.db_session.rollback()
            raise e
        except Exception as e:
            self.db_session.rollback()
            raise ValueError(f"Erro ao atualizar insumo: {str(e)}")
    
    def delete(self, insumo_id: UUID) -> bool:
        """
        Remove logicamente um insumo (marcando como inativo).
        
        Args:
            insumo_id: ID do insumo a ser removido
            
        Returns:
            bool: True se removido com sucesso, False se não encontrado
        """
        try:
            # Buscar insumo
            insumo = (
                self.db_session.query(Insumo)
                .filter(Insumo.id == insumo_id, Insumo.is_active == True)
                .first()
            )
            
            if not insumo:
                return False
            
            # Desativar insumo (remoção lógica)
            insumo.is_active = False
            insumo.updated_at = datetime.utcnow()
            
            # Commit
            self.db_session.commit()
            
            return True
            
        except Exception as e:
            self.db_session.rollback()
            raise ValueError(f"Erro ao remover insumo: {str(e)}")
    
    def update_stock(self, insumo_id: UUID, quantidade: int, tipo_movimento: str) -> InsumoEntity:
        """
        Atualiza o estoque de um insumo.
        
        Args:
            insumo_id: ID do insumo a ter estoque atualizado
            quantidade: Quantidade a ser adicionada ou removida
            tipo_movimento: 'entrada' para adicionar ou 'saida' para remover
            
        Returns:
            InsumoEntity: Entidade atualizada
            
        Raises:
            ValueError: Se o insumo não existir ou operação inválida
        """
        try:
            # Validar tipo de movimento
            if tipo_movimento not in ['entrada', 'saida']:
                raise ValueError("Tipo de movimento deve ser 'entrada' ou 'saida'")
            
            # Buscar insumo
            insumo = (
                self.db_session.query(Insumo)
                .options(joinedload(Insumo.modules_used))
                .filter(Insumo.id == insumo_id, Insumo.is_active == True)
                .first()
            )
            
            if not insumo:
                raise ValueError(f"Insumo com ID {insumo_id} não encontrado")
            
            # Converter para entidade para aplicar lógica de negócio
            entity = InsumoAdapter.to_entity(insumo)
            
            # Atualizar estoque usando métodos da entidade
            if tipo_movimento == 'entrada':
                entity.adicionar_estoque(quantidade)
            else:
                entity.reduzir_estoque(quantidade)
            
            # Sincronizar modelo com entidade
            insumo.estoque_atual = entity.estoque_atual
            insumo.updated_at = datetime.utcnow()
            
            # Commit
            self.db_session.commit()
            
            # Retornar entidade atualizada
            return InsumoAdapter.to_entity(insumo)
            
        except ValueError as e:
            self.db_session.rollback()
            raise e
        except Exception as e:
            self.db_session.rollback()
            raise ValueError(f"Erro ao atualizar estoque do insumo: {str(e)}")