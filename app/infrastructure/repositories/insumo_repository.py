"""
Implementação de repositório para Insumos usando SQLAlchemy.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.db.models.insumo import Insumo
from app.db.models.module import Module
from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface
from app.infrastructure.adapters.insumo_adapter import InsumoAdapter


class SQLAlchemyInsumoRepository(InsumoRepositoryInterface):
    """
    Implementação do repositório de insumos usando SQLAlchemy.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, insumo: InsumoEntity) -> InsumoEntity:
        """
        Cria um novo insumo no banco de dados.
        
        Args:
            insumo: Entidade de insumo a ser criada
            
        Returns:
            InsumoEntity: Entidade de insumo criada com ID gerado
        """
        # Converte a entidade de domínio para um modelo ORM
        insumo_orm = InsumoAdapter.to_orm(insumo)
        
        # Associa os módulos, se houver módulos
        if insumo.modules_used:
            # Verifica se o modelo de módulo existe no banco de dados
            try:
                modules = self.db_session.query(Module).filter(
                    Module.id.in_(insumo.modules_used)
                ).all()
                # Associar apenas se encontrou os módulos
                if modules:
                    insumo_orm.modules = modules
            except Exception as e:
                # Em caso de erro na associação de módulos, apenas registra e continua
                print(f"Erro ao associar módulos: {str(e)}")
                pass
        
        # Adiciona à sessão e persiste
        self.db_session.add(insumo_orm)
        self.db_session.commit()
        self.db_session.refresh(insumo_orm)
        
        # Converte o modelo ORM de volta para uma entidade de domínio
        return InsumoAdapter.to_entity(insumo_orm)

    def get_by_id(self, insumo_id: UUID) -> Optional[InsumoEntity]:
        """
        Busca um insumo pelo ID.
        
        Args:
            insumo_id: UUID do insumo
            
        Returns:
            Optional[InsumoEntity]: Entidade de insumo se encontrada, None caso contrário
        """
        insumo_orm = self.db_session.query(Insumo).filter(
            Insumo.id == insumo_id,
            Insumo.is_active == True
        ).first()
        
        if not insumo_orm:
            return None
        
        return InsumoAdapter.to_entity(insumo_orm)

    def list_insumos(self, 
                     skip: int = 0, 
                     limit: int = 100,
                     subscriber_id: Optional[UUID] = None,
                     filters: Optional[Dict[str, Any]] = None) -> List[InsumoEntity]:
        """
        Lista insumos com paginação e filtros opcionais.
        
        Args:
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros a retornar
            subscriber_id: Filtrar por ID do assinante (multitenant)
            filters: Filtros adicionais como categoria, nome, etc.
            
        Returns:
            List[InsumoEntity]: Lista de entidades de insumo
        """
        query = self.db_session.query(Insumo).filter(Insumo.is_active == True)
        
        # Aplicar filtro de subscriber_id (multitenant)
        if subscriber_id:
            query = query.filter(Insumo.subscriber_id == subscriber_id)
        
        # Aplicar filtros adicionais
        if filters:
            filter_conditions = []
            
            if 'nome' in filters and filters['nome']:
                filter_conditions.append(Insumo.nome.ilike(f"%{filters['nome']}%"))
            
            if 'categoria' in filters and filters['categoria']:
                filter_conditions.append(Insumo.categoria == filters['categoria'])
            
            if 'fornecedor' in filters and filters['fornecedor']:
                filter_conditions.append(Insumo.fornecedor.ilike(f"%{filters['fornecedor']}%"))
            
            if 'codigo_referencia' in filters and filters['codigo_referencia']:
                filter_conditions.append(Insumo.codigo_referencia.ilike(f"%{filters['codigo_referencia']}%"))
            
            if 'estoque_baixo' in filters and filters['estoque_baixo']:
                # Filtrar insumos com estoque abaixo do mínimo
                query = query.filter(Insumo.estoque_atual < Insumo.estoque_minimo)
            
            if 'module_id' in filters and filters['module_id']:
                try:
                    # Filtrar insumos associados a um módulo específico
                    query = query.join(Insumo.modules).filter(Module.id == filters['module_id'])
                except Exception as e:
                    # Em caso de erro, ignorar este filtro
                    print(f"Erro ao filtrar por módulo: {str(e)}")
                    pass
            
            if filter_conditions:
                query = query.filter(or_(*filter_conditions))
        
        # Aplicar paginação
        query = query.order_by(Insumo.nome).offset(skip).limit(limit)
        
        # Executar a consulta
        insumos_orm = query.all()
        
        # Converter para entidades de domínio
        return [InsumoAdapter.to_entity(insumo) for insumo in insumos_orm]

    def update(self, insumo_id: UUID, data: Dict[str, Any]) -> Optional[InsumoEntity]:
        """
        Atualiza um insumo existente.
        
        Args:
            insumo_id: UUID do insumo a ser atualizado
            data: Dicionário com os campos a serem atualizados
            
        Returns:
            Optional[InsumoEntity]: Entidade de insumo atualizada se encontrada, None caso contrário
        """
        # Buscar o insumo no banco de dados
        insumo_orm = self.db_session.query(Insumo).filter(
            Insumo.id == insumo_id,
            Insumo.is_active == True
        ).first()
        
        if not insumo_orm:
            return None
        
        # Atualizar os módulos se estiverem incluídos nos dados
        if 'modules_used' in data and data['modules_used'] is not None:
            try:
                modules = self.db_session.query(Module).filter(
                    Module.id.in_(data['modules_used'])
                ).all()
                insumo_orm.modules = modules
            except Exception as e:
                # Em caso de erro na associação de módulos, apenas registra e continua
                print(f"Erro ao atualizar módulos: {str(e)}")
                pass
            
            # Remover do dicionário para não processar novamente
            del data['modules_used']
        
        # Atualizar os campos do ORM
        InsumoAdapter.update_orm_from_dict(insumo_orm, data)
        
        # Persistir as alterações
        self.db_session.commit()
        self.db_session.refresh(insumo_orm)
        
        # Retornar a entidade atualizada
        return InsumoAdapter.to_entity(insumo_orm)

    def delete(self, insumo_id: UUID) -> bool:
        """
        Exclui logicamente um insumo (soft delete).
        
        Args:
            insumo_id: UUID do insumo a ser excluído
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        # Buscar o insumo no banco de dados
        insumo_orm = self.db_session.query(Insumo).filter(
            Insumo.id == insumo_id,
            Insumo.is_active == True
        ).first()
        
        if not insumo_orm:
            return False
        
        # Marcar como inativo (soft delete)
        insumo_orm.is_active = False
        insumo_orm.updated_at = datetime.utcnow()
        
        # Persistir as alterações
        self.db_session.commit()
        
        return True

    def count(self, 
              subscriber_id: Optional[UUID] = None,
              filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Conta o número total de insumos com filtros opcionais.
        
        Args:
            subscriber_id: Filtrar por ID do assinante (multitenant)
            filters: Filtros adicionais
            
        Returns:
            int: Número total de insumos
        """
        query = self.db_session.query(Insumo).filter(Insumo.is_active == True)
        
        # Aplicar filtro de subscriber_id (multitenant)
        if subscriber_id:
            query = query.filter(Insumo.subscriber_id == subscriber_id)
        
        # Aplicar filtros adicionais
        if filters:
            filter_conditions = []
            
            if 'nome' in filters and filters['nome']:
                filter_conditions.append(Insumo.nome.ilike(f"%{filters['nome']}%"))
            
            if 'categoria' in filters and filters['categoria']:
                filter_conditions.append(Insumo.categoria == filters['categoria'])
            
            if 'fornecedor' in filters and filters['fornecedor']:
                filter_conditions.append(Insumo.fornecedor.ilike(f"%{filters['fornecedor']}%"))
            
            if 'codigo_referencia' in filters and filters['codigo_referencia']:
                filter_conditions.append(Insumo.codigo_referencia.ilike(f"%{filters['codigo_referencia']}%"))
            
            if 'estoque_baixo' in filters and filters['estoque_baixo']:
                # Filtrar insumos com estoque abaixo do mínimo
                query = query.filter(Insumo.estoque_atual < Insumo.estoque_minimo)
            
            if 'module_id' in filters and filters['module_id']:
                try:
                    # Filtrar insumos associados a um módulo específico
                    query = query.join(Insumo.modules).filter(Module.id == filters['module_id'])
                except Exception as e:
                    # Em caso de erro, ignorar este filtro
                    print(f"Erro ao filtrar por módulo na contagem: {str(e)}")
                    pass
            
            if filter_conditions:
                query = query.filter(or_(*filter_conditions))
        
        # Executar a contagem
        return query.count()