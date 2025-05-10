"""
Serviço para operações CRUD de planos
"""

from typing import Optional, Dict, Any, List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc, asc, or_
from sqlalchemy.orm import Session

from app.db.models import Plan, Module, PlanModule, Segment
from app.schemas.plan import PlanCreate, PlanUpdate, PaginatedPlanResponse, PlanModuleCreate


class PlanService:
    """
    Serviço para operações relacionadas a planos
    Implementa as regras de negócio e acesso a dados
    """

    @staticmethod
    def get_plans(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filter_params: Optional[Dict[str, Any]] = None
    ) -> PaginatedPlanResponse:
        """
        Retorna uma lista paginada de planos com opção de filtros
        
        Args:
            db: Sessão do banco de dados
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros para retornar (paginação)
            filter_params: Parâmetros para filtragem (opcional)
            
        Returns:
            PaginatedPlanResponse: Lista paginada de planos
        """
        query = db.query(Plan)
        
        # Aplicar filtros se houver
        if filter_params:
            if name := filter_params.get("name"):
                query = query.filter(Plan.name.ilike(f"%{name}%"))
            
            if segment_id := filter_params.get("segment_id"):
                query = query.filter(Plan.segment_id == segment_id)
                
            if is_active := filter_params.get("is_active"):
                if isinstance(is_active, bool):
                    query = query.filter(Plan.is_active == is_active)
        
        # Contar total antes de aplicar paginação
        total = query.count()
        
        # Aplicar paginação
        query = query.order_by(asc(Plan.name)).offset(skip).limit(limit)
        
        # Executar a consulta
        plans = query.all()
        
        # Para cada plano, buscar os relacionamentos necessários para a resposta
        for plan in plans:
            # Carregar os módulos vinculados ao plano
            db.query(PlanModule).filter(PlanModule.plan_id == plan.id).all()
        
        return PaginatedPlanResponse(
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            size=limit,
            items=plans
        )
    
    @staticmethod
    def get_plan_by_id(db: Session, plan_id: UUID) -> Optional[Plan]:
        """
        Busca um plano pelo ID
        
        Args:
            db: Sessão do banco de dados
            plan_id: ID do plano
            
        Returns:
            Optional[Plan]: Plano encontrado ou None
        """
        return db.query(Plan).filter(Plan.id == plan_id).first()
    
    @staticmethod
    def get_plan_by_name(db: Session, name: str) -> Optional[Plan]:
        """
        Busca um plano pelo nome
        
        Args:
            db: Sessão do banco de dados
            name: Nome do plano
            
        Returns:
            Optional[Plan]: Plano encontrado ou None
        """
        return db.query(Plan).filter(Plan.name == name).first()
    
    @staticmethod
    def validate_segment(db: Session, segment_id: UUID) -> Segment:
        """
        Valida se o segmento existe
        
        Args:
            db: Sessão do banco de dados
            segment_id: ID do segmento
            
        Returns:
            Segment: Segmento encontrado
            
        Raises:
            HTTPException: Se o segmento não for encontrado
        """
        segment = db.query(Segment).filter(Segment.id == segment_id).first()
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Segmento com ID {segment_id} não encontrado"
            )
        return segment
    
    @staticmethod
    def validate_modules(db: Session, module_ids: List[UUID]) -> List[Module]:
        """
        Valida se os módulos existem
        
        Args:
            db: Sessão do banco de dados
            module_ids: Lista de IDs de módulos
            
        Returns:
            List[Module]: Lista de módulos encontrados
            
        Raises:
            HTTPException: Se algum módulo não for encontrado
        """
        modules = db.query(Module).filter(Module.id.in_(module_ids)).all()
        found_ids = [str(module.id) for module in modules]
        
        missing_ids = []
        for module_id in module_ids:
            if str(module_id) not in found_ids:
                missing_ids.append(str(module_id))
        
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Módulos com os seguintes IDs não foram encontrados: {', '.join(missing_ids)}"
            )
            
        return modules
    
    @staticmethod
    def create_plan(db: Session, plan_data: PlanCreate) -> Plan:
        """
        Cria um novo plano
        
        Args:
            db: Sessão do banco de dados
            plan_data: Dados do novo plano
            
        Returns:
            Plan: Plano criado
            
        Raises:
            HTTPException: Se o nome já estiver em uso ou se segmento/módulos não forem encontrados
        """
        # Verificar se já existe plano com esse nome
        existing_plan = PlanService.get_plan_by_name(db, plan_data.name)
        if existing_plan:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe um plano com o nome '{plan_data.name}'"
            )
        
        # Validar se o segmento existe
        PlanService.validate_segment(db, plan_data.segment_id)
        
        # Obter IDs dos módulos
        module_ids = [module_data.module_id for module_data in plan_data.modules]
        
        # Validar se os módulos existem
        if module_ids:
            PlanService.validate_modules(db, module_ids)
        
        # Criar plano
        plan_dict = plan_data.model_dump(exclude={"modules"})
        db_plan = Plan(**plan_dict)
        db.add(db_plan)
        db.flush()  # Para gerar o ID do plano
        
        # Criar associações com módulos
        for module_data in plan_data.modules:
            # Criar relacionamento com cada módulo
            plan_module = PlanModule(
                plan_id=db_plan.id,
                module_id=module_data.module_id,
                price=0 if module_data.is_free else module_data.price,
                is_free=module_data.is_free,
                trial_days=module_data.trial_days
            )
            db.add(plan_module)
        
        db.commit()
        db.refresh(db_plan)
        
        return db_plan
    
    @staticmethod
    def update_plan(db: Session, plan_id: UUID, plan_data: PlanUpdate) -> Optional[Plan]:
        """
        Atualiza um plano existente
        
        Args:
            db: Sessão do banco de dados
            plan_id: ID do plano a ser atualizado
            plan_data: Dados a serem atualizados
            
        Returns:
            Optional[Plan]: Plano atualizado ou None se não for encontrado
            
        Raises:
            HTTPException: Se o nome já estiver em uso por outro plano ou segmento/módulos não forem encontrados
        """
        db_plan = PlanService.get_plan_by_id(db, plan_id)
        if not db_plan:
            return None
        
        # Verificar se o novo nome já está em uso (se houver alteração)
        if plan_data.name and plan_data.name != db_plan.name:
            existing_plan = PlanService.get_plan_by_name(db, plan_data.name)
            if existing_plan and existing_plan.id != plan_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Já existe um plano com o nome '{plan_data.name}'"
                )
        
        # Validar segmento se for atualizar
        if plan_data.segment_id:
            PlanService.validate_segment(db, plan_data.segment_id)
        
        # Atualizar dados básicos do plano
        update_data = plan_data.model_dump(exclude={"modules"}, exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_plan, key, value)
        
        # Atualizar módulos se especificado
        if plan_data.modules is not None:
            # Obter IDs dos módulos
            module_ids = [module_data.module_id for module_data in plan_data.modules]
            
            # Validar se os módulos existem
            if module_ids:
                PlanService.validate_modules(db, module_ids)
            
            # Remover todos os módulos atuais
            db.query(PlanModule).filter(PlanModule.plan_id == plan_id).delete()
            db.flush()
            
            # Adicionar novos módulos
            for module_data in plan_data.modules:
                plan_module = PlanModule(
                    plan_id=plan_id,
                    module_id=module_data.module_id,
                    price=0 if module_data.is_free else module_data.price,
                    is_free=module_data.is_free,
                    trial_days=module_data.trial_days
                )
                db.add(plan_module)
        
        db.commit()
        db.refresh(db_plan)
        
        return db_plan
    
    @staticmethod
    def delete_plan(db: Session, plan_id: UUID) -> bool:
        """
        Exclui um plano pelo ID
        
        Args:
            db: Sessão do banco de dados
            plan_id: ID do plano a ser excluído
            
        Returns:
            bool: True se o plano foi excluído, False se não foi encontrado
        """
        db_plan = PlanService.get_plan_by_id(db, plan_id)
        if not db_plan:
            return False
        
        # Remover o plano (a cascata removerá as relações com módulos)
        db.delete(db_plan)
        db.commit()
        
        return True
        
    @staticmethod
    def toggle_plan_status(db: Session, plan_id: UUID, activate: bool) -> Optional[Plan]:
        """
        Ativa ou desativa um plano
        
        Args:
            db: Sessão do banco de dados
            plan_id: ID do plano
            activate: True para ativar, False para desativar
            
        Returns:
            Optional[Plan]: Plano atualizado ou None se não for encontrado
        """
        db_plan = PlanService.get_plan_by_id(db, plan_id)
        if not db_plan:
            return None
            
        db_plan.is_active = activate
        db.commit()
        db.refresh(db_plan)
        
        return db_plan