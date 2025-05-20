"""
Implementação do repositório de insumos utilizando SQLAlchemy.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union
from uuid import UUID

from sqlalchemy import and_, or_, func, text
from sqlalchemy.orm import Session, contains_eager

from app.db.models.insumo import Insumo, InsumoModuleAssociation
from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface
from app.domain.insumo.value_objects.modulo_association import ModuloAssociation
from app.infrastructure.adapters.insumo_adapter import InsumoAdapter


class SQLAlchemyInsumoRepository(InsumoRepositoryInterface):
    """
    Implementação do repositório de insumos utilizando SQLAlchemy para persistência.
    
    Esta classe concreta implementa as operações definidas na interface,
    utilizando o SQLAlchemy como ORM para acesso ao banco de dados.
    """
    
    def __init__(self, db_session: Session):
        """
        Inicializa o repositório com uma sessão de banco de dados.
        
        Args:
            db_session: Sessão SQLAlchemy para o banco de dados
        """
        self.db = db_session
        self.adapter = InsumoAdapter()
    
    def create(self, insumo: InsumoEntity) -> InsumoEntity:
        """
        Cria um novo insumo no banco de dados.
        
        Args:
            insumo: Entidade de insumo a ser criada
            
        Returns:
            InsumoEntity: Entidade criada com ID gerado
            
        Raises:
            ValueError: Se ocorrer um erro durante a criação
        """
        try:
            # Converter entidade para modelo
            insumo_model = self.adapter.to_model(insumo)
            
            # Adicionar à sessão
            self.db.add(insumo_model)
            self.db.flush()  # Para obter o ID gerado
            
            # Processar associações de módulos, se houver
            if insumo.modules_used:
                associations = self.adapter.create_module_associations(
                    insumo.modules_used, insumo_model.id
                )
                for assoc in associations:
                    self.db.add(assoc)
                self.db.flush()
            
            # Commit da transação
            self.db.commit()
            
            # Recarregar o modelo para obter as associações
            self.db.refresh(insumo_model)
            
            # Converter modelo atualizado para entidade
            return self.adapter.to_entity(insumo_model)
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Erro ao criar insumo: {str(e)}")
    
    def get_by_id(self, insumo_id: UUID) -> Optional[InsumoEntity]:
        """
        Busca um insumo pelo ID.
        
        Args:
            insumo_id: ID do insumo a buscar
            
        Returns:
            Optional[InsumoEntity]: Entidade encontrada ou None
        """
        try:
            # Buscar insumo com suas associações
            insumo_model = self.db.query(Insumo).filter(
                Insumo.id == insumo_id,
                Insumo.is_active == True
            ).first()
            
            if not insumo_model:
                return None
            
            # Mapear associações de módulos
            self._map_module_associations(insumo_model.id)
            
            # Converter para entidade e retornar
            return self.adapter.to_entity(insumo_model)
            
        except Exception as e:
            raise ValueError(f"Erro ao buscar insumo: {str(e)}")
    
    def _map_module_associations(self, insumo_id: UUID) -> None:
        """
        Carrega associações de módulos para um insumo.
        
        Args:
            insumo_id: ID do insumo
        """
        try:
            # Pré-carregar associações com módulos para melhorar performance
            associations = self.db.query(InsumoModuleAssociation).filter(
                InsumoModuleAssociation.insumo_id == insumo_id
            ).all()
            
            # Obter IDs de módulos para carregar nomes
            module_ids = [assoc.module_id for assoc in associations]
            
            # Carregar nomes de módulos se necessário (se tabela Module existir)
            if module_ids and hasattr(InsumoModuleAssociation, 'module'):
                # Esta parte depende da estrutura da tabela Module
                pass
            
        except Exception as e:
            # Logar erro, mas não interromper operação
            print(f"Erro ao mapear associações de módulos: {str(e)}")
    
    def list_by_subscriber(
        self, 
        subscriber_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Lista insumos de um assinante com paginação e filtros opcionais.
        
        Args:
            subscriber_id: ID do assinante
            skip: Quantos registros pular
            limit: Limite de registros a retornar
            filters: Filtros a aplicar (nome, categoria, etc.)
            
        Returns:
            Dict[str, Any]: Dicionário com itens e informações de paginação
        """
        try:
            # Iniciar query base
            query = self.db.query(Insumo).filter(
                Insumo.is_active == True
            )
            
            # Aplicar filtro por assinante
            if subscriber_id:
                query = query.filter(Insumo.subscriber_id == subscriber_id)
            
            # Aplicar filtros adicionais, se fornecidos
            query, total = self._apply_filters(query, filters or {})
            
            # Calcular total de registros para paginação
            if total is None:
                total = query.count()
            
            # Aplicar paginação
            items = query.order_by(Insumo.nome).offset(skip).limit(limit).all()
            
            # Converter modelos para entidades
            entities = [self.adapter.to_entity(item) for item in items]
            
            # Construir resposta
            return {
                "items": entities,
                "total": total,
                "page": skip // limit + 1 if limit > 0 else 1,
                "pages": (total + limit - 1) // limit if limit > 0 else 1,
                "size": len(entities)
            }
            
        except Exception as e:
            raise ValueError(f"Erro ao listar insumos: {str(e)}")
    
    def _apply_filters(
        self, 
        query, 
        filters: Dict[str, Any]
    ) -> Tuple[Any, Optional[int]]:
        """
        Aplica filtros a uma query de insumos.
        
        Args:
            query: Query SQLAlchemy base
            filters: Dicionário de filtros a aplicar
            
        Returns:
            Tuple[Any, Optional[int]]: Query filtrada e total de registros (se calculado)
        """
        total = None
        
        # Filtro por nome (busca por substring)
        if "nome" in filters and filters["nome"]:
            search_term = f"%{filters['nome']}%"
            query = query.filter(Insumo.nome.ilike(search_term))
        
        # Filtro por categoria (exata)
        if "categoria" in filters and filters["categoria"]:
            query = query.filter(Insumo.categoria == filters["categoria"])
        
        # Filtro por fornecedor (busca por substring)
        if "fornecedor" in filters and filters["fornecedor"]:
            search_term = f"%{filters['fornecedor']}%"
            query = query.filter(Insumo.fornecedor.ilike(search_term))
        
        # Filtro por estoque baixo
        if "estoque_baixo" in filters and filters["estoque_baixo"] is not None:
            if filters["estoque_baixo"]:
                query = query.filter(Insumo.estoque_atual < Insumo.estoque_minimo)
        
        # Filtro por módulo
        if "module_id" in filters and filters["module_id"]:
            query = query.join(InsumoModuleAssociation).filter(
                InsumoModuleAssociation.module_id == filters["module_id"]
            )
        
        return query, total
    
    def update(self, insumo_id: UUID, data: Dict[str, Any]) -> Optional[InsumoEntity]:
        """
        Atualiza um insumo existente.
        
        Args:
            insumo_id: ID do insumo a atualizar
            data: Dicionário com os campos a atualizar
            
        Returns:
            Optional[InsumoEntity]: Entidade atualizada ou None
            
        Raises:
            ValueError: Se ocorrer um erro durante a atualização
        """
        try:
            # Buscar insumo existente
            insumo_model = self.db.query(Insumo).filter(
                Insumo.id == insumo_id,
                Insumo.is_active == True
            ).first()
            
            if not insumo_model:
                return None
            
            # Atualizar campos do modelo
            self.adapter.update_from_dict(insumo_model, data)
            
            # Atualizar associações de módulos, se fornecidas
            if "modules_used" in data and data["modules_used"]:
                # Remover associações existentes
                self.db.query(InsumoModuleAssociation).filter(
                    InsumoModuleAssociation.insumo_id == insumo_id
                ).delete()
                
                # Criar novas associações
                associations = self.adapter.create_module_associations(
                    data["modules_used"], insumo_id
                )
                for assoc in associations:
                    self.db.add(assoc)
            
            # Commit das alterações
            self.db.commit()
            
            # Recarregar o modelo para obter as associações atualizadas
            self.db.refresh(insumo_model)
            
            # Converter modelo atualizado para entidade
            return self.adapter.to_entity(insumo_model)
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Erro ao atualizar insumo: {str(e)}")
    
    def delete(self, insumo_id: UUID) -> bool:
        """
        Exclui logicamente um insumo (soft delete).
        
        Args:
            insumo_id: ID do insumo a excluir
            
        Returns:
            bool: True se excluído com sucesso, False caso contrário
            
        Raises:
            ValueError: Se ocorrer um erro durante a exclusão
        """
        try:
            # Buscar insumo existente
            insumo_model = self.db.query(Insumo).filter(
                Insumo.id == insumo_id,
                Insumo.is_active == True
            ).first()
            
            if not insumo_model:
                return False
            
            # Marcar como inativo (soft delete)
            insumo_model.is_active = False
            insumo_model.updated_at = datetime.utcnow()
            
            # Commit das alterações
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Erro ao excluir insumo: {str(e)}")
    
    def update_estoque(
        self, 
        insumo_id: UUID, 
        quantidade: int,
        tipo_movimento: str,
        observacao: Optional[str] = None
    ) -> Optional[InsumoEntity]:
        """
        Atualiza o estoque de um insumo (entrada ou saída).
        
        Args:
            insumo_id: ID do insumo
            quantidade: Quantidade a adicionar/remover
            tipo_movimento: 'entrada' ou 'saida'
            observacao: Observação opcional sobre o movimento
            
        Returns:
            Optional[InsumoEntity]: Entidade atualizada ou None
            
        Raises:
            ValueError: Se os parâmetros forem inválidos ou estoque insuficiente
        """
        try:
            # Validações iniciais
            if quantidade <= 0:
                raise ValueError("Quantidade deve ser maior que zero")
            
            if tipo_movimento not in ["entrada", "saida"]:
                raise ValueError("Tipo de movimento deve ser 'entrada' ou 'saida'")
            
            # Buscar insumo existente
            insumo_model = self.db.query(Insumo).filter(
                Insumo.id == insumo_id,
                Insumo.is_active == True
            ).first()
            
            if not insumo_model:
                return None
            
            # Converter modelo para entidade para usar lógica de domínio
            insumo_entity = self.adapter.to_entity(insumo_model)
            
            # Aplicar movimento de estoque
            if tipo_movimento == "entrada":
                insumo_entity.adicionar_estoque(quantidade)
            else:  # saida
                insumo_entity.reduzir_estoque(quantidade)
            
            # Atualizar modelo com valores da entidade
            insumo_model.estoque_atual = insumo_entity.estoque_atual
            insumo_model.updated_at = insumo_entity.updated_at
            
            # Aqui poderíamos registrar o movimento em uma tabela de histórico
            # if observacao:
            #    registrar_movimento_estoque(...)
            
            # Commit das alterações
            self.db.commit()
            
            # Converter modelo atualizado para entidade
            return self.adapter.to_entity(insumo_model)
            
        except ValueError as e:
            self.db.rollback()
            raise ValueError(str(e))
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Erro ao atualizar estoque: {str(e)}")