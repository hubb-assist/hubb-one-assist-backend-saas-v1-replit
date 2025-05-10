"""
Serviço para operações CRUD de usuários
"""

import uuid
from typing import Optional, List, Dict, Any, Union

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import bcrypt

from app.db.models import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse, PaginatedUserResponse

class UserService:
    """
    Serviço para operações relacionadas a usuários
    Implementa as regras de negócio e acesso a dados
    """
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Gera hash da senha usando bcrypt
        
        Args:
            password: Senha em texto puro
            
        Returns:
            str: Hash da senha
        """
        # Gerar salt e hash com bcrypt
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        return hashed_password.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifica se a senha em texto puro corresponde ao hash
        
        Args:
            plain_password: Senha em texto puro
            hashed_password: Hash da senha armazenado
            
        Returns:
            bool: True se a senha corresponder ao hash, False caso contrário
        """
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    @staticmethod
    def get_users(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filter_params: Optional[Dict[str, Any]] = None
    ) -> PaginatedUserResponse:
        """
        Retorna uma lista paginada de usuários com opção de filtros
        
        Args:
            db: Sessão do banco de dados
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros para retornar (paginação)
            filter_params: Parâmetros para filtragem (opcional)
            
        Returns:
            PaginatedUserResponse: Lista paginada de usuários
        """
        query = db.query(User)
        
        # Aplicar filtros se fornecidos
        if filter_params:
            for key, value in filter_params.items():
                if value is not None and hasattr(User, key):
                    query = query.filter(getattr(User, key) == value)
        
        # Contar total antes de aplicar paginação
        total = query.count()
        
        # Aplicar paginação
        users = query.offset(skip).limit(limit).all()
        
        # Converter os objetos User para dicionários e depois para UserResponse
        user_responses = [UserResponse.model_validate(user) for user in users]
        
        # Criar resposta paginada
        return PaginatedUserResponse(
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            size=limit,
            items=user_responses
        )
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
        """
        Busca um usuário pelo ID
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário
            
        Returns:
            Optional[User]: Usuário encontrado ou None
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Busca um usuário pelo email
        
        Args:
            db: Sessão do banco de dados
            email: Email do usuário
            
        Returns:
            Optional[User]: Usuário encontrado ou None
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Cria um novo usuário
        
        Args:
            db: Sessão do banco de dados
            user_data: Dados do novo usuário
            
        Returns:
            User: Usuário criado
            
        Raises:
            HTTPException: Se o email já estiver em uso
        """
        # Verificar se email já existe
        if UserService.get_user_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso"
            )
        
        # Criar usuário com hash da senha
        hashed_password = UserService.get_password_hash(user_data.senha)
        
        db_user = User(
            nome=user_data.nome,
            email=user_data.email,
            senha_hashed=hashed_password,
            role=user_data.role,
            is_active=user_data.is_active
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: uuid.UUID, user_data: UserUpdate) -> Optional[User]:
        """
        Atualiza um usuário existente
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário a ser atualizado
            user_data: Dados a serem atualizados
            
        Returns:
            Optional[User]: Usuário atualizado ou None se não for encontrado
            
        Raises:
            HTTPException: Se o email já estiver em uso por outro usuário
        """
        # Buscar usuário existente
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        # Verificar se o novo email já está em uso por outro usuário
        if user_data.email is not None and user_data.email != db_user.email:
            existing_user = UserService.get_user_by_email(db, user_data.email)
            if existing_user is not None and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já está em uso por outro usuário"
                )
        
        # Atualizar campos fornecidos
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Tratar senha separadamente para aplicar hash
        if "senha" in update_data:
            hashed_password = UserService.get_password_hash(update_data.pop("senha"))
            setattr(db_user, "senha_hashed", hashed_password)
        
        # Atualizar os outros campos
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: uuid.UUID) -> bool:
        """
        Exclui um usuário pelo ID
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário a ser excluído
            
        Returns:
            bool: True se o usuário foi excluído, False se não foi encontrado
        """
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        
        return True
    
    @staticmethod
    def create_admin_user(db: Session) -> None:
        """
        Cria o usuário admin padrão se ele não existir
        
        Args:
            db: Sessão do banco de dados
        """
        # Verificar se o usuário admin já existe
        admin_email = "admin@hubbassist.com"
        existing_admin = UserService.get_user_by_email(db, admin_email)
        
        if not existing_admin:
            # Criar usuário admin
            admin_data = UserCreate(
                nome="Admin",
                email=admin_email,
                senha="admin123",
                role=UserRole.SUPER_ADMIN,
                is_active=True
            )
            
            UserService.create_user(db, admin_data)