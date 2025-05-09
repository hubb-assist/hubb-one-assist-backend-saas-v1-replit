from typing import Dict, List, Optional, Tuple, Union

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.db.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:
    """
    Repository class for User model - handles database operations
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID
        
        Args:
            user_id: The user ID
            
        Returns:
            The user if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email
        
        Args:
            email: The user email
            
        Returns:
            The user if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()
    
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
        query = self.db.query(User)
        
        if filters:
            filter_conditions = []
            
            # Apply filters if provided
            if filters.get("name"):
                filter_conditions.append(User.name.ilike(f"%{filters['name']}%"))
            
            if filters.get("email"):
                filter_conditions.append(User.email.ilike(f"%{filters['email']}%"))
            
            if filters.get("role"):
                try:
                    role = UserRole(filters["role"])
                    filter_conditions.append(User.role == role)
                except ValueError:
                    pass  # Invalid role, ignore this filter
            
            if filter_conditions:
                query = query.filter(and_(*filter_conditions))
        
        total = query.count()
        users = query.order_by(User.name).offset(skip).limit(limit).all()
        
        return users, total
    
    def create_user(self, user_create: UserCreate, password_hash: str) -> User:
        """
        Create a new user
        
        Args:
            user_create: UserCreate schema with user data
            password_hash: Hashed password
            
        Returns:
            The created user
        """
        db_user = User(
            name=user_create.name,
            email=user_create.email,
            password_hash=password_hash,
            role=user_create.role,
            is_active=True
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def update_user(self, user_id: int, user_update: UserUpdate, password_hash: Optional[str] = None) -> Optional[User]:
        """
        Update a user
        
        Args:
            user_id: The ID of the user to update
            user_update: UserUpdate schema with updated fields
            password_hash: Optional new password hash
            
        Returns:
            The updated user or None if not found
        """
        db_user = self.get_user_by_id(user_id)
        
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        if password_hash:
            update_data["password_hash"] = password_hash
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user
        
        Args:
            user_id: The ID of the user to delete
            
        Returns:
            True if the user was deleted, False otherwise
        """
        db_user = self.get_user_by_id(user_id)
        
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        
        return True
