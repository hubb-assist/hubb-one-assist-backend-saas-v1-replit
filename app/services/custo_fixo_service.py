from uuid import UUID
from datetime import date
from typing import Optional, Dict, Any, List, Union
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.models_cost_fixed import CostFixed
from app.schemas.custo_fixo import CustoFixoCreate, CustoFixoUpdate, CustoFixoResponse, CustoFixoList


class CustoFixoService:
    """
    Serviço para gerenciamento de custos fixos.
    """
    
    @staticmethod
    def get_custos_fixos(
        db: Session,
        current_user: Any,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Retorna uma lista paginada de custos fixos do assinante.
        
        Args:
            db: Sessão do banco de dados
            current_user: Usuário autenticado
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros para retornar (paginação)
            date_from: Data inicial para filtro
            date_to: Data final para filtro
            
        Returns:
            Dicionário com a lista de custos fixos e informações de paginação
        """
        # Recuperar subscriber_id do usuário autenticado
        subscriber_id = getattr(current_user, "subscriber_id", None)
        if not subscriber_id:
            return {"items": [], "total": 0, "skip": skip, "limit": limit}
        
        # Consulta base
        query = db.query(CostFixed).filter(
            CostFixed.subscriber_id == subscriber_id,
            CostFixed.is_active == True
        )
        
        # Aplicar filtros de data se fornecidos
        if date_from:
            query = query.filter(CostFixed.data >= date_from)
            
        if date_to:
            query = query.filter(CostFixed.data <= date_to)
        
        # Contar total de registros (para paginação)
        total = query.count()
        
        # Ordenar e aplicar paginação
        custos = query.order_by(desc(CostFixed.data)).offset(skip).limit(limit).all()
        
        # Converter para schema de resposta
        items = [CustoFixoResponse.model_validate(custo) for custo in custos]
        
        return CustoFixoList(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
    
    @staticmethod
    def get_custo_fixo_by_id(
        db: Session,
        custo_fixo_id: UUID,
        current_user: Any
    ) -> Optional[CustoFixoResponse]:
        """
        Recupera um custo fixo pelo ID.
        
        Args:
            db: Sessão do banco de dados
            custo_fixo_id: ID do custo fixo
            current_user: Usuário autenticado
            
        Returns:
            Custo fixo encontrado ou None
        """
        # Recuperar subscriber_id do usuário autenticado
        subscriber_id = getattr(current_user, "subscriber_id", None)
        if not subscriber_id:
            return None
        
        # Buscar o custo fixo no banco de dados
        custo = db.query(CostFixed).filter(
            CostFixed.id == custo_fixo_id,
            CostFixed.subscriber_id == subscriber_id,
            CostFixed.is_active == True
        ).first()
        
        if not custo:
            return None
        
        # Converter para schema de resposta
        return CustoFixoResponse.model_validate(custo)
    
    @staticmethod
    def create_custo_fixo(
        db: Session,
        custo_fixo: CustoFixoCreate,
        current_user: Any
    ) -> Optional[CustoFixoResponse]:
        """
        Cria um novo custo fixo.
        
        Args:
            db: Sessão do banco de dados
            custo_fixo: Dados do custo fixo a ser criado
            current_user: Usuário autenticado
            
        Returns:
            Custo fixo criado ou None se falhar
        """
        # Recuperar subscriber_id do usuário autenticado
        subscriber_id = getattr(current_user, "subscriber_id", None)
        if not subscriber_id:
            return None
        
        # Criar objeto do banco de dados
        db_custo = CostFixed(
            nome=custo_fixo.nome,
            valor=custo_fixo.valor,
            data=custo_fixo.data,
            observacoes=custo_fixo.observacoes,
            subscriber_id=subscriber_id
        )
        
        # Salvar no banco de dados
        db.add(db_custo)
        db.commit()
        db.refresh(db_custo)
        
        # Converter para schema de resposta
        return CustoFixoResponse.model_validate(db_custo)
    
    @staticmethod
    def update_custo_fixo(
        db: Session,
        custo_fixo_id: UUID,
        custo_fixo: CustoFixoUpdate,
        current_user: Any
    ) -> Optional[CustoFixoResponse]:
        """
        Atualiza um custo fixo existente.
        
        Args:
            db: Sessão do banco de dados
            custo_fixo_id: ID do custo fixo a ser atualizado
            custo_fixo: Dados para atualização
            current_user: Usuário autenticado
            
        Returns:
            Custo fixo atualizado ou None se não encontrado
        """
        # Recuperar subscriber_id do usuário autenticado
        subscriber_id = getattr(current_user, "subscriber_id", None)
        if not subscriber_id:
            return None
        
        # Buscar o custo fixo no banco de dados
        db_custo = db.query(CostFixed).filter(
            CostFixed.id == custo_fixo_id,
            CostFixed.subscriber_id == subscriber_id,
            CostFixed.is_active == True
        ).first()
        
        if not db_custo:
            return None
        
        # Converter para dicionário e remover valores None
        update_data = custo_fixo.model_dump(exclude_unset=True, exclude_none=True)
        
        # Atualizar os campos
        for key, value in update_data.items():
            setattr(db_custo, key, value)
        
        # Salvar no banco de dados
        db.commit()
        db.refresh(db_custo)
        
        # Converter para schema de resposta
        return CustoFixoResponse.model_validate(db_custo)
    
    @staticmethod
    def delete_custo_fixo(
        db: Session,
        custo_fixo_id: UUID,
        current_user: Any
    ) -> bool:
        """
        Remove logicamente um custo fixo (define is_active como False).
        
        Args:
            db: Sessão do banco de dados
            custo_fixo_id: ID do custo fixo a ser removido
            current_user: Usuário autenticado
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        # Recuperar subscriber_id do usuário autenticado
        subscriber_id = getattr(current_user, "subscriber_id", None)
        if not subscriber_id:
            return False
        
        # Buscar o custo fixo no banco de dados
        db_custo = db.query(CostFixed).filter(
            CostFixed.id == custo_fixo_id,
            CostFixed.subscriber_id == subscriber_id,
            CostFixed.is_active == True
        ).first()
        
        if not db_custo:
            return False
        
        # Remover logicamente (definir is_active como False)
        db_custo.is_active = False
        
        # Salvar no banco de dados
        db.commit()
        
        return True