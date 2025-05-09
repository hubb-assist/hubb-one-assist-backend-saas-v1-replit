from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.db.models.user import User
from app.db.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """
    Service class for user-related operations
    Implements business logic and uses the repository for data access
    """
    
    def __init__(self, db: Session):
        self.repository = UserRepository(db)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID
        
        Args:
            user_id: The user ID
            
        Returns:
            The user if found, None otherwise
        """
        return self.repository.get_user_by_id(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email
        
        Args:
            email: The user email
            
        Returns:
            The user if found, None otherwise
        """
        return self.repository.get_user_by_email(email)
    
    def get_users(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, str]] = None
    ) -> Tuple[List[User], int]:
        """
        Get a list of users with pagination and optional filtering
        
        Args:
            skip: Records to skip (for pagination)
            limit: Maximum number of records to return
            filters: Optional filters (name, email, role)
            
        Returns:
            Tuple containing list of users and total count
        """
        return self.repository.get_users(skip=skip, limit=limit, filters=filters)
    
    def create_user(self, user_create: UserCreate) -> User:
        """
        Create a new user
        
        Args:
            user_create: UserCreate schema with user data
            
        Returns:
            The created user
        """
        password_hash = get_password_hash(user_create.password)
        return self.repository.create_user(user_create, password_hash)
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """
        Update a user
        
        Args:
            user_id: The ID of the user to update
            user_update: UserUpdate schema with updated fields
            
        Returns:
            The updated user or None if not found
        """
        password_hash = None
        
        if user_update.password:
            password_hash = get_password_hash(user_update.password)
        
        return self.repository.update_user(user_id, user_update, password_hash)
    
    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user
        
        Args:
            user_id: The ID of the user to delete
            
        Returns:
            True if the user was deleted, False otherwise
        """
        return self.repository.delete_user(user_id)
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user
        
        Args:
            email: User email
            password: User password
            
        Returns:
            The user if authentication is successful, None otherwise
        """
        user = self.get_user_by_email(email)
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
