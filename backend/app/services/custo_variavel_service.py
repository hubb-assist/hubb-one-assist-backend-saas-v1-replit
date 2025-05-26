from uuid import UUID
from datetime import date
from typing import Optional, Any, List
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.models_cost_variable import CostVariable
from app.schemas.custo_variavel import (
    CustoVariavelCreate, 
    CustoVariavelUpdate, 
    CustoVariavelResponse, 
    CustoVariavelList
)


class CustoVariavelService:
    """
    Serviço para gerenciamento de custos variáveis.
    """
    
    @staticmethod
    def get_custos_variaveis(
        db: Session,
        current_user: Any,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> CustoVariavelList:
        """
        Retorna uma lista paginada de custos variáveis do assinante.
        
        Args:
            db: Sessão do banco de dados
            current_user: Usuário autenticado
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros para retornar (paginação)
            date_from: Data inicial para filtro
            date_to: Data final para filtro
            
        Returns:
            Lista paginada de custos variáveis
        """
        # Recuperar subscriber_id do usuário autenticado
        subscriber_id = getattr(current_user, "subscriber_id", None)
        if not subscriber_id:
            return CustoVariavelList(items=[], total=0, skip=skip, limit=limit)
        
        # Consulta base
        query = db.query(CostVariable).filter(
            CostVariable.subscriber_id == subscriber_id,
            CostVariable.is_active == True
        )
        
        # Aplicar filtros de data se fornecidos
        if date_from:
            query = query.filter(CostVariable.data >= date_from)
            
        if date_to:
            query = query.filter(CostVariable.data <= date_to)
        
        # Contar total de registros (para paginação)
        total = query.count()
        
        # Ordenar e aplicar paginação
        custos = query.order_by(desc(CostVariable.data)).offset(skip).limit(limit).all()
        
        # Converter para schema de resposta e calcular o valor total
        items = []
        for custo in custos:
            custo_dict = {
                "id": custo.id,
                "subscriber_id": custo.subscriber_id,
                "nome": custo.nome,
                "valor_unitario": custo.valor_unitario,
                "quantidade": custo.quantidade,
                "data": custo.data,
                "observacoes": custo.observacoes,
                "is_active": custo.is_active,
                "created_at": custo.created_at,
                "updated_at": custo.updated_at,
                "valor_total": custo.valor_unitario * custo.quantidade
            }
            items.append(CustoVariavelResponse.model_validate(custo_dict))
        
        return CustoVariavelList(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
    
    @staticmethod
    def get_custo_variavel_by_id(
        db: Session,
        custo_variavel_id: UUID,
        current_user: Any
    ) -> Optional[CustoVariavelResponse]:
        """
        Recupera um custo variável pelo ID.
        
        Args:
            db: Sessão do banco de dados
            custo_variavel_id: ID do custo variável
            current_user: Usuário autenticado
            
        Returns:
            Custo variável encontrado ou None
        """
        # Recuperar subscriber_id do usuário autenticado
        subscriber_id = getattr(current_user, "subscriber_id", None)
        if not subscriber_id:
            return None
        
        # Buscar o custo variável no banco de dados
        custo = db.query(CostVariable).filter(
            CostVariable.id == custo_variavel_id,
            CostVariable.subscriber_id == subscriber_id,
            CostVariable.is_active == True
        ).first()
        
        if not custo:
            return None
        
        # Converter para schema de resposta e calcular o valor total
        custo_dict = {
            "id": custo.id,
            "subscriber_id": custo.subscriber_id,
            "nome": custo.nome,
            "valor_unitario": custo.valor_unitario,
            "quantidade": custo.quantidade,
            "data": custo.data,
            "observacoes": custo.observacoes,
            "is_active": custo.is_active,
            "created_at": custo.created_at,
            "updated_at": custo.updated_at,
            "valor_total": custo.valor_unitario * custo.quantidade
        }
        
        return CustoVariavelResponse.model_validate(custo_dict)
    
    @staticmethod
    def create_custo_variavel(
        db: Session,
        custo_variavel: CustoVariavelCreate,
        current_user: Any
    ) -> Optional[CustoVariavelResponse]:
        """
        Cria um novo custo variável.
        
        Args:
            db: Sessão do banco de dados
            custo_variavel: Dados do custo variável a ser criado
            current_user: Usuário autenticado
            
        Returns:
            Custo variável criado ou None se falhar
        """
        # Recuperar subscriber_id do usuário autenticado
        subscriber_id = getattr(current_user, "subscriber_id", None)
        if not subscriber_id:
            return None
        
        # Criar objeto do banco de dados
        db_custo = CostVariable(
            nome=custo_variavel.nome,
            valor_unitario=custo_variavel.valor_unitario,
            quantidade=custo_variavel.quantidade,
            data=custo_variavel.data,
            observacoes=custo_variavel.observacoes,
            subscriber_id=subscriber_id
        )
        
        # Salvar no banco de dados
        db.add(db_custo)
        db.commit()
        db.refresh(db_custo)
        
        # Converter para schema de resposta e calcular o valor total
        custo_dict = {
            "id": db_custo.id,
            "subscriber_id": db_custo.subscriber_id,
            "nome": db_custo.nome,
            "valor_unitario": db_custo.valor_unitario,
            "quantidade": db_custo.quantidade,
            "data": db_custo.data,
            "observacoes": db_custo.observacoes,
            "is_active": db_custo.is_active,
            "created_at": db_custo.created_at,
            "updated_at": db_custo.updated_at,
            "valor_total": db_custo.valor_unitario * db_custo.quantidade
        }
        
        return CustoVariavelResponse.model_validate(custo_dict)
    
    @staticmethod
    def update_custo_variavel(
        db: Session,
        custo_variavel_id: UUID,
        custo_variavel: CustoVariavelUpdate,
        current_user: Any
    ) -> Optional[CustoVariavelResponse]:
        """
        Atualiza um custo variável existente.
        
        Args:
            db: Sessão do banco de dados
            custo_variavel_id: ID do custo variável a ser atualizado
            custo_variavel: Dados para atualização
            current_user: Usuário autenticado
            
        Returns:
            Custo variável atualizado ou None se não encontrado
        """
        # Recuperar subscriber_id do usuário autenticado
        subscriber_id = getattr(current_user, "subscriber_id", None)
        if not subscriber_id:
            return None
        
        # Buscar o custo variável no banco de dados
        db_custo = db.query(CostVariable).filter(
            CostVariable.id == custo_variavel_id,
            CostVariable.subscriber_id == subscriber_id,
            CostVariable.is_active == True
        ).first()
        
        if not db_custo:
            return None
        
        # Converter para dicionário e remover valores None
        update_data = custo_variavel.model_dump(exclude_unset=True, exclude_none=True)
        
        # Atualizar os campos
        for key, value in update_data.items():
            setattr(db_custo, key, value)
        
        # Salvar no banco de dados
        db.commit()
        db.refresh(db_custo)
        
        # Converter para schema de resposta e calcular o valor total
        custo_dict = {
            "id": db_custo.id,
            "subscriber_id": db_custo.subscriber_id,
            "nome": db_custo.nome,
            "valor_unitario": db_custo.valor_unitario,
            "quantidade": db_custo.quantidade,
            "data": db_custo.data,
            "observacoes": db_custo.observacoes,
            "is_active": db_custo.is_active,
            "created_at": db_custo.created_at,
            "updated_at": db_custo.updated_at,
            "valor_total": db_custo.valor_unitario * db_custo.quantidade
        }
        
        return CustoVariavelResponse.model_validate(custo_dict)
    
    @staticmethod
    def delete_custo_variavel(
        db: Session,
        custo_variavel_id: UUID,
        current_user: Any
    ) -> bool:
        """
        Remove logicamente um custo variável (define is_active como False).
        
        Args:
            db: Sessão do banco de dados
            custo_variavel_id: ID do custo variável a ser removido
            current_user: Usuário autenticado
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        # Recuperar subscriber_id do usuário autenticado
        subscriber_id = getattr(current_user, "subscriber_id", None)
        if not subscriber_id:
            return False
        
        # Buscar o custo variável no banco de dados
        db_custo = db.query(CostVariable).filter(
            CostVariable.id == custo_variavel_id,
            CostVariable.subscriber_id == subscriber_id,
            CostVariable.is_active == True
        ).first()
        
        if not db_custo:
            return False
        
        # Remover logicamente (definir is_active como False)
        db_custo.is_active = False
        
        # Salvar no banco de dados
        db.commit()
        
        return True