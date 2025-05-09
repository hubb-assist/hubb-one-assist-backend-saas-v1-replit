from typing import Generic, List, Optional, TypeVar

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationParams:
    """
    Pagination parameters for list endpoints
    """
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(10, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.limit = limit
        self.skip = (page - 1) * limit


class PaginationResponse(BaseModel, Generic[T]):
    """
    Pagination response model
    """
    data: List[T]
    total: int
    page: int
    limit: int
    
    @property
    def pages(self) -> int:
        """Calculate total number of pages"""
        return (self.total + self.limit - 1) // self.limit if self.limit > 0 else 0
    
    model_config = ConfigDict(from_attributes=True)
