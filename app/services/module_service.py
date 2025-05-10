"""
Serviço para operações CRUD de módulos funcionais
"""

from typing import Optional, Dict, Any, List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc, asc, or_
from sqlalchemy.orm import Session

from app.db.models import Module
from app.schemas.module import ModuleCreate, ModuleUpdate, PaginatedModuleResponse


class ModuleService:
    """
    Serviço para operações relacionadas a módulos funcionais
    Implementa as regras de negócio e acesso a dados
    """

    @staticmethod
    def get_modules(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filter_params: Optional[Dict[str, Any]] = None
    ) -> PaginatedModuleResponse:
        """
        Retorna uma lista paginada de módulos com opção de filtros
        
        Args:
            db: Sessão do banco de dados
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros para retornar (paginação)
            filter_params: Parâmetros para filtragem (opcional)
            
        Returns:
            PaginatedModuleResponse: Lista paginada de módulos
        """
        query = db.query(Module)
        
        # Aplicar filtros se houver
        if filter_params:
            if nome := filter_params.get("nome"):
                query = query.filter(Module.nome.ilike(f"%{nome}%"))
            
            if is_active := filter_params.get("is_active"):
                if isinstance(is_active, bool):
                    query = query.filter(Module.is_active == is_active)
        
        # Contar total antes de aplicar paginação
        total = query.count()
        
        # Aplicar paginação
        query = query.order_by(asc(Module.nome)).offset(skip).limit(limit)
        
        # Mapear resultados para o schema de resposta
        modules = query.all()
        
        return PaginatedModuleResponse(
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            size=limit,
            items=modules
        )
    
    @staticmethod
    def get_module_by_id(db: Session, module_id: UUID) -> Optional[Module]:
        """
        Busca um módulo pelo ID
        
        Args:
            db: Sessão do banco de dados
            module_id: ID do módulo
            
        Returns:
            Optional[Module]: Módulo encontrado ou None
        """
        return db.query(Module).filter(Module.id == module_id).first()
    
    @staticmethod
    def get_module_by_nome(db: Session, nome: str) -> Optional[Module]:
        """
        Busca um módulo pelo nome
        
        Args:
            db: Sessão do banco de dados
            nome: Nome do módulo
            
        Returns:
            Optional[Module]: Módulo encontrado ou None
        """
        return db.query(Module).filter(Module.nome == nome).first()
    
    @staticmethod
    def create_module(db: Session, module_data: ModuleCreate) -> Module:
        """
        Cria um novo módulo
        
        Args:
            db: Sessão do banco de dados
            module_data: Dados do novo módulo
            
        Returns:
            Module: Módulo criado
            
        Raises:
            HTTPException: Se o nome já estiver em uso
        """
        # Verificar se já existe módulo com esse nome
        existing_module = ModuleService.get_module_by_nome(db, module_data.nome)
        if existing_module:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe um módulo com o nome '{module_data.nome}'"
            )
        
        # Criar novo módulo
        db_module = Module(**module_data.model_dump())
        db.add(db_module)
        db.commit()
        db.refresh(db_module)
        
        return db_module
    
    @staticmethod
    def update_module(db: Session, module_id: UUID, module_data: ModuleUpdate) -> Optional[Module]:
        """
        Atualiza um módulo existente
        
        Args:
            db: Sessão do banco de dados
            module_id: ID do módulo a ser atualizado
            module_data: Dados a serem atualizados
            
        Returns:
            Optional[Module]: Módulo atualizado ou None se não for encontrado
            
        Raises:
            HTTPException: Se o nome já estiver em uso por outro módulo
        """
        db_module = ModuleService.get_module_by_id(db, module_id)
        if not db_module:
            return None
        
        # Verificar se o novo nome já está em uso (se houver alteração)
        if module_data.nome and module_data.nome != db_module.nome:
            existing_module = ModuleService.get_module_by_nome(db, module_data.nome)
            if existing_module and existing_module.id != module_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Já existe um módulo com o nome '{module_data.nome}'"
                )
        
        # Atualizar apenas os campos não nulos
        update_data = module_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_module, key, value)
        
        db.commit()
        db.refresh(db_module)
        
        return db_module
    
    @staticmethod
    def delete_module(db: Session, module_id: UUID) -> bool:
        """
        Exclui um módulo pelo ID
        
        Args:
            db: Sessão do banco de dados
            module_id: ID do módulo a ser excluído
            
        Returns:
            bool: True se o módulo foi excluído, False se não foi encontrado
        """
        db_module = ModuleService.get_module_by_id(db, module_id)
        if not db_module:
            return False
        
        db.delete(db_module)
        db.commit()
        
        return True
        
    @staticmethod
    def toggle_module_status(db: Session, module_id: UUID, activate: bool) -> Optional[Module]:
        """
        Ativa ou desativa um módulo
        
        Args:
            db: Sessão do banco de dados
            module_id: ID do módulo
            activate: True para ativar, False para desativar
            
        Returns:
            Optional[Module]: Módulo atualizado ou None se não for encontrado
        """
        db_module = ModuleService.get_module_by_id(db, module_id)
        if not db_module:
            return None
            
        db_module.is_active = activate
        db.commit()
        db.refresh(db_module)
        
        return db_module