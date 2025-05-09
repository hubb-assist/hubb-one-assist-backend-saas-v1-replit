from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_db
from app.core.security import check_permissions
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.services.user_service import UserService
from app.utils.pagination import PaginationParams, PaginationResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=PaginationResponse[UserOut])
async def list_users(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user),
    pagination: PaginationParams = Depends(),
    name: Optional[str] = Query(None, description="Filter by name"),
    email: Optional[str] = Query(None, description="Filter by email"),
    role: Optional[str] = Query(None, description="Filter by role"),
) -> Any:
    """
    List all users with pagination and optional filtering.
    Only accessible by authorized users.
    """
    check_permissions(current_user, ["SUPER_ADMIN", "DIRETOR"])
    
    user_service = UserService(db)
    users, total = user_service.get_users(
        skip=pagination.skip,
        limit=pagination.limit,
        filters={
            "name": name,
            "email": email,
            "role": role
        }
    )
    
    return PaginationResponse(
        data=users,
        total=total,
        page=pagination.page,
        limit=pagination.limit
    )


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific user by ID.
    Only accessible by authorized users or the user themselves.
    """
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Allow users to see their own profile or if they have proper permissions
    if current_user.id != user_id and current_user.role not in ["SUPER_ADMIN", "DIRETOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return user


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user),
) -> Any:
    """
    Create a new user.
    Only accessible by SUPER_ADMIN or DIRETOR.
    """
    check_permissions(current_user, ["SUPER_ADMIN", "DIRETOR"])
    
    user_service = UserService(db)
    
    # Check if user with same email already exists
    if user_service.get_user_by_email(user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return user_service.create_user(user_in)


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user),
) -> Any:
    """
    Update a user.
    Users can update their own information, but only SUPER_ADMIN or DIRETOR can update other users.
    """
    user_service = UserService(db)
    current_user_db = user_service.get_user_by_id(user_id)
    
    if not current_user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Allow users to update their own profile or if they have proper permissions
    if current_user.id != user_id and current_user.role not in ["SUPER_ADMIN", "DIRETOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Only SUPER_ADMIN can change roles
    if user_in.role is not None and current_user.role != "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to change user role"
        )
    
    return user_service.update_user(user_id, user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user),
):
    """
    Delete a user.
    Only accessible by SUPER_ADMIN.
    """
    check_permissions(current_user, ["SUPER_ADMIN"])
    
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_service.delete_user(user_id)
