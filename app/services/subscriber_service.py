"""
Serviço para operações CRUD de assinantes
"""

from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models import Subscriber, User, Segment, Plan, UserRole
from app.schemas.subscriber import SubscriberCreate, SubscriberUpdate
from app.services.user_service import UserService


class SubscriberService:
    """
    Serviço para operações relacionadas a assinantes
    Implementa as regras de negócio e acesso a dados
    """
    
    @staticmethod
    def get_subscribers(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filter_params: Optional[Dict[str, Any]] = None,
        current_user: Optional[User] = None
    ) -> Dict[str, Any]:
        """
        Retorna uma lista paginada de assinantes com opção de filtros
        
        Args:
            db: Sessão do banco de dados
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros para retornar (paginação)
            filter_params: Parâmetros para filtragem (opcional)
            current_user: Usuário autenticado (para aplicar filtro por subscriber_id)
            
        Returns:
            Dict[str, Any]: Dicionário com total, página, tamanho e itens
        """
        query = db.query(Subscriber)
        
        # Aplicar filtro por subscriber_id se o usuário for DONO_ASSINANTE
        # Importamos a função aqui para evitar circular imports
        if current_user:
            from app.core.dependencies import apply_subscriber_filter
            query = apply_subscriber_filter(query, current_user, Subscriber)
        
        # Aplicar filtros se fornecidos
        if filter_params:
            if filter_params.get("name"):
                query = query.filter(Subscriber.name.ilike(f"%{filter_params['name']}%"))
            if filter_params.get("clinic_name"):
                query = query.filter(Subscriber.clinic_name.ilike(f"%{filter_params['clinic_name']}%"))
            if filter_params.get("email"):
                query = query.filter(Subscriber.email.ilike(f"%{filter_params['email']}%"))
            if filter_params.get("document"):
                query = query.filter(Subscriber.document == filter_params["document"])
            if filter_params.get("segment_id"):
                query = query.filter(Subscriber.segment_id == filter_params["segment_id"])
            if filter_params.get("plan_id"):
                query = query.filter(Subscriber.plan_id == filter_params["plan_id"])
            if filter_params.get("is_active") is not None:
                query = query.filter(Subscriber.is_active == filter_params["is_active"])
                
        # Contar total antes de aplicar paginação
        total = query.count()
        
        # Aplicar paginação
        subscribers = query.order_by(Subscriber.created_at.desc()).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "page": skip // limit + 1,
            "size": limit,
            "items": subscribers
        }
    
    @staticmethod
    def get_subscriber_by_id(db: Session, subscriber_id: UUID, current_user: Optional[User] = None) -> Optional[Subscriber]:
        """
        Busca um assinante pelo ID
        
        Args:
            db: Sessão do banco de dados
            subscriber_id: ID do assinante
            current_user: Usuário autenticado (para aplicar filtro por subscriber_id)
            
        Returns:
            Optional[Subscriber]: Assinante encontrado ou None
        """
        query = db.query(Subscriber).filter(Subscriber.id == subscriber_id)
        
        # Aplicar filtro por subscriber_id se o usuário for DONO_ASSINANTE
        if current_user:
            # SUPER_ADMIN e DIRETOR podem acessar qualquer assinante
            if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.DIRETOR]:
                # DONO_ASSINANTE só pode acessar seu próprio assinante
                if current_user.role == UserRole.DONO_ASSINANTE and current_user.subscriber_id:
                    # Garante que o subscriber_id solicitado seja o mesmo associado ao usuário
                    if current_user.subscriber_id != subscriber_id:
                        return None
        
        return query.first()
    
    @staticmethod
    def get_subscriber_by_email(db: Session, email: str) -> Optional[Subscriber]:
        """
        Busca um assinante pelo e-mail
        
        Args:
            db: Sessão do banco de dados
            email: E-mail do assinante
            
        Returns:
            Optional[Subscriber]: Assinante encontrado ou None
        """
        return db.query(Subscriber).filter(Subscriber.email == email).first()
    
    @staticmethod
    def get_subscriber_by_document(db: Session, document: str) -> Optional[Subscriber]:
        """
        Busca um assinante pelo documento (CPF/CNPJ)
        
        Args:
            db: Sessão do banco de dados
            document: Documento do assinante
            
        Returns:
            Optional[Subscriber]: Assinante encontrado ou None
        """
        return db.query(Subscriber).filter(Subscriber.document == document).first()
    
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
    def validate_plan(db: Session, plan_id: Optional[UUID]) -> Optional[Plan]:
        """
        Valida se o plano existe
        
        Args:
            db: Sessão do banco de dados
            plan_id: ID do plano (pode ser None)
            
        Returns:
            Optional[Plan]: Plano encontrado ou None se plan_id for None
            
        Raises:
            HTTPException: Se o plano não for encontrado
        """
        if plan_id is None:
            return None
            
        plan = db.query(Plan).filter(Plan.id == plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plano com ID {plan_id} não encontrado"
            )
        return plan
    
    @staticmethod
    def create_subscriber(db: Session, subscriber_data: SubscriberCreate) -> Subscriber:
        """
        Cria um novo assinante e seu usuário administrador
        
        Args:
            db: Sessão do banco de dados
            subscriber_data: Dados do novo assinante
            
        Returns:
            Subscriber: Assinante criado
            
        Raises:
            HTTPException: Se houver conflito com dados existentes ou recursos não encontrados
        """
        # Verificar se já existe assinante com o mesmo email
        existing_email = SubscriberService.get_subscriber_by_email(db, subscriber_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe um assinante com o email '{subscriber_data.email}'"
            )
        
        # Verificar se já existe assinante com o mesmo documento
        existing_document = SubscriberService.get_subscriber_by_document(db, subscriber_data.document)
        if existing_document:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe um assinante com o documento '{subscriber_data.document}'"
            )
        
        # Validar se o segmento existe
        SubscriberService.validate_segment(db, subscriber_data.segment_id)
        
        # Validar se o plano existe (se fornecido)
        if subscriber_data.plan_id:
            SubscriberService.validate_plan(db, subscriber_data.plan_id)
        
        # Criar o assinante
        subscriber_dict = subscriber_data.model_dump(exclude={"admin_password"})
        db_subscriber = Subscriber(**subscriber_dict)
        db.add(db_subscriber)
        db.flush()  # Gera o ID do assinante
        
        # Criar usuário administrador para o assinante
        from app.schemas.user import UserCreate
        admin_user_data = UserCreate(
            name=subscriber_data.name,
            email=subscriber_data.email,
            password=subscriber_data.admin_password,
            role=UserRole.DONO_ASSINANTE,
            is_active=True
        )
        
        admin_user = UserService.create_user(db, admin_user_data, subscriber_id=db_subscriber.id)
        
        db.commit()
        db.refresh(db_subscriber)
        
        return db_subscriber
    
    @staticmethod
    def update_subscriber(db: Session, subscriber_id: UUID, subscriber_data: SubscriberUpdate) -> Optional[Subscriber]:
        """
        Atualiza um assinante existente
        
        Args:
            db: Sessão do banco de dados
            subscriber_id: ID do assinante
            subscriber_data: Dados a serem atualizados
            
        Returns:
            Optional[Subscriber]: Assinante atualizado ou None se não for encontrado
            
        Raises:
            HTTPException: Se houver conflito com dados existentes ou recursos não encontrados
        """
        # Buscar o assinante
        db_subscriber = SubscriberService.get_subscriber_by_id(db, subscriber_id)
        if not db_subscriber:
            return None
        
        # Verificar se email está sendo alterado e se já existe
        if subscriber_data.email and subscriber_data.email != db_subscriber.email:
            existing_email = SubscriberService.get_subscriber_by_email(db, subscriber_data.email)
            if existing_email and existing_email.id != subscriber_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Já existe um assinante com o email '{subscriber_data.email}'"
                )
        
        # Verificar se documento está sendo alterado e se já existe
        if subscriber_data.document and subscriber_data.document != db_subscriber.document:
            existing_document = SubscriberService.get_subscriber_by_document(db, subscriber_data.document)
            if existing_document and existing_document.id != subscriber_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Já existe um assinante com o documento '{subscriber_data.document}'"
                )
        
        # Validar segmento se estiver sendo atualizado
        if subscriber_data.segment_id:
            try:
                SubscriberService.validate_segment(db, subscriber_data.segment_id)
            except HTTPException as e:
                # Se o segmento for inválido, manteremos o segmento existente
                print(f"Segmento inválido na atualização: {str(e)}")
                subscriber_data.segment_id = db_subscriber.segment_id
        else:
            # Se segment_id não foi fornecido, mantenha o valor existente
            print(f"Segmento não fornecido, mantendo existente: {db_subscriber.segment_id}")
            subscriber_data.segment_id = db_subscriber.segment_id
        
        # Validar plano se estiver sendo atualizado
        if subscriber_data.plan_id:
            try:
                SubscriberService.validate_plan(db, subscriber_data.plan_id)
            except HTTPException as e:
                # Se o plano for inválido, manteremos o plano existente
                print(f"Plano inválido na atualização: {str(e)}")
                subscriber_data.plan_id = db_subscriber.plan_id
        else:
            # Se plan_id não foi fornecido, mantenha o valor existente
            print(f"Plano não fornecido, mantendo existente: {db_subscriber.plan_id}")
            subscriber_data.plan_id = db_subscriber.plan_id
        
        # Atualizar os dados
        update_data = subscriber_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_subscriber, key, value)
        
        db.commit()
        db.refresh(db_subscriber)
        
        return db_subscriber
    
    @staticmethod
    def delete_subscriber(db: Session, subscriber_id: UUID) -> bool:
        """
        Exclui ou desativa um assinante
        
        Args:
            db: Sessão do banco de dados
            subscriber_id: ID do assinante
            
        Returns:
            bool: True se o assinante foi desativado/excluído, False se não foi encontrado
        """
        subscriber = SubscriberService.get_subscriber_by_id(db, subscriber_id)
        if not subscriber:
            return False
        
        # Opção 1: Exclusão lógica (desativar)
        subscriber.is_active = False
        
        # Desativar também os usuários associados
        for user in subscriber.users:
            user.is_active = False
        
        db.commit()
        
        return True
    
    @staticmethod
    def toggle_subscriber_status(db: Session, subscriber_id: UUID, activate: bool) -> Optional[Subscriber]:
        """
        Ativa ou desativa um assinante
        
        Args:
            db: Sessão do banco de dados
            subscriber_id: ID do assinante
            activate: True para ativar, False para desativar
            
        Returns:
            Optional[Subscriber]: Assinante atualizado ou None se não for encontrado
        """
        subscriber = SubscriberService.get_subscriber_by_id(db, subscriber_id)
        if not subscriber:
            return None
            
        subscriber.is_active = activate
        
        # Atualizar também o status dos usuários associados
        for user in subscriber.users:
            user.is_active = activate
        
        db.commit()
        db.refresh(subscriber)
        
        return subscriber