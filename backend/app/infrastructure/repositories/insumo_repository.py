"""
Implementação do repositório de Insumos usando SQLAlchemy.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.db.models_insumo import Insumo, InsumoModuleAssociation, InsumoMovimentacao
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
    
    def update_stock(self, insumo_id: UUID, quantidade: int, tipo_movimento: str, 
                    motivo: Optional[str] = None, observacao: Optional[str] = None, 
                    usuario_id: Optional[UUID] = None) -> InsumoEntity:
        """
        Atualiza o estoque de um insumo.
        
        Args:
            insumo_id: ID do insumo a ter estoque atualizado
            quantidade: Quantidade a ser adicionada ou removida
            tipo_movimento: 'entrada' para adicionar ou 'saida' para remover
            motivo: Motivo da movimentação de estoque (opcional)
            observacao: Observação adicional sobre a movimentação (opcional)
            usuario_id: ID do usuário que realizou a movimentação (opcional)
            
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
            
            # Armazenar o estoque anterior para o histórico
            estoque_anterior = insumo.estoque_atual
            
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
            
            # Criar o registro de movimentação no histórico
            movimentacao = InsumoMovimentacao(
                insumo_id=insumo_id,
                quantidade=quantidade,
                tipo_movimento=tipo_movimento,
                motivo=motivo,
                estoque_anterior=estoque_anterior,
                estoque_resultante=insumo.estoque_atual,
                observacao=observacao,
                usuario_id=usuario_id,
                subscriber_id=insumo.subscriber_id
            )
            
            # Adicionar movimentação ao banco
            self.db_session.add(movimentacao)
            
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
            
    def get_movimentacoes(
        self, 
        subscriber_id: UUID, 
        insumo_id: Optional[UUID] = None,
        tipo_movimento: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Lista o histórico de movimentações de estoque de insumos com filtros.
        
        Args:
            subscriber_id: ID do assinante (isolamento multitenant)
            insumo_id: Filtrar por ID do insumo específico (opcional)
            tipo_movimento: Filtrar por tipo de movimento ('entrada' ou 'saida') (opcional)
            data_inicio: Filtrar por data inicial (opcional)
            data_fim: Filtrar por data final (opcional)
            skip: Quantos registros pular (paginação)
            limit: Limite de registros a retornar (paginação)
            
        Returns:
            Tuple[List[Dict[str, Any]], int]: Lista de movimentações e contagem total
        """
        try:
            # Consulta base para obter movimentações com o nome do insumo
            query = (
                self.db_session.query(
                    InsumoMovimentacao,
                    Insumo.nome.label('insumo_nome'),
                    Insumo.categoria.label('insumo_categoria'),
                    Insumo.unidade_medida.label('insumo_unidade_medida')
                )
                .join(Insumo, InsumoMovimentacao.insumo_id == Insumo.id)
                .filter(InsumoMovimentacao.subscriber_id == subscriber_id)
            )
            
            # Aplicar filtros adicionais se fornecidos
            if insumo_id:
                query = query.filter(InsumoMovimentacao.insumo_id == insumo_id)
                
            if tipo_movimento:
                query = query.filter(InsumoMovimentacao.tipo_movimento == tipo_movimento)
                
            if data_inicio:
                query = query.filter(InsumoMovimentacao.created_at >= data_inicio)
                
            if data_fim:
                query = query.filter(InsumoMovimentacao.created_at <= data_fim)
                
            # Consulta para a contagem total
            count_query = query.with_entities(func.count(InsumoMovimentacao.id))
            total_count = count_query.scalar() or 0
            
            # Aplicar ordenação e paginação
            query = (
                query
                .order_by(desc(InsumoMovimentacao.created_at))
                .offset(skip)
                .limit(limit)
            )
            
            # Executar consulta
            results = query.all()
            
            # Transformar resultados em dicionários para serializar facilmente
            movimentacoes = []
            for row in results:
                movimentacao = row[0]  # InsumoMovimentacao
                insumo_nome = row[1]   # Insumo.nome
                insumo_categoria = row[2]  # Insumo.categoria
                insumo_unidade_medida = row[3]  # Insumo.unidade_medida
                
                # Criar dicionário com todos os dados
                mov_dict = {
                    'id': movimentacao.id,
                    'insumo_id': movimentacao.insumo_id,
                    'quantidade': movimentacao.quantidade,
                    'tipo_movimento': movimentacao.tipo_movimento,
                    'motivo': movimentacao.motivo,
                    'estoque_anterior': movimentacao.estoque_anterior,
                    'estoque_resultante': movimentacao.estoque_resultante,
                    'observacao': movimentacao.observacao,
                    'usuario_id': movimentacao.usuario_id,
                    'subscriber_id': movimentacao.subscriber_id,
                    'created_at': movimentacao.created_at,
                    'insumo_nome': insumo_nome,
                    'insumo_categoria': insumo_categoria,
                    'insumo_unidade_medida': insumo_unidade_medida
                }
                
                movimentacoes.append(mov_dict)
                
            return movimentacoes, total_count
            
        except Exception as e:
            raise ValueError(f"Erro ao obter histórico de movimentações: {str(e)}")