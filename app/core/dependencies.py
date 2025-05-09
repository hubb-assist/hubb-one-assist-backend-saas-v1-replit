from typing import Any, Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import check_permissions
from app.db.session import SessionLocal
from app.schemas.user import TokenData
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_db() -> Generator:
    """
    Get a database session.
    
    Yields:
        A database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> Any:
    """
    Get the current user from the JWT token.
    
    Args:
        db: Database session
        token: JWT token
        
    Returns:
        The current user
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenData(user_id=int(payload["sub"]), token_type=payload.get("type"))
        
        if token_data.token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_service = UserService(db)
    user = user_service.get_user_by_id(token_data.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


def get_current_active_user(
    current_user: Any = Depends(get_current_user),
) -> Any:
    """
    Get the current active user.
    
    Args:
        current_user: The current user
        
    Returns:
        The current active user
        
    Raises:
        HTTPException: If the user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user


def check_admin_permission(current_user: Any = Depends(get_current_active_user)) -> Any:
    """
    Check if the current user has admin permissions.
    
    Args:
        current_user: The current user
        
    Returns:
        The current user if they have admin permissions
        
    Raises:
        HTTPException: If the user doesn't have admin permissions
    """
    check_permissions(current_user, ["SUPER_ADMIN"])
    return current_user


def check_manager_permission(current_user: Any = Depends(get_current_active_user)) -> Any:
    """
    Check if the current user has manager permissions.
    
    Args:
        current_user: The current user
        
    Returns:
        The current user if they have manager permissions
        
    Raises:
        HTTPException: If the user doesn't have manager permissions
    """
    check_permissions(current_user, ["SUPER_ADMIN", "DIRETOR"])
    return current_user
