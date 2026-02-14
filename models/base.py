# models/base.py
# Model fondasi: base response, pagination, error handling

from pydantic import BaseModel, Field
from typing import Optional, Any, List
from datetime import datetime


class BaseResponse(BaseModel):
    """Response dasar untuk semua endpoint API"""
    success: bool = True
    message: str = "OK"
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseResponse):
    """Response error standar"""
    success: bool = False
    error_code: Optional[str] = None
    detail: Optional[str] = None


class PaginationMeta(BaseModel):
    """Metadata pagination"""
    page: int = 1
    per_page: int = 20
    total_items: int
    total_pages: int


class PaginatedResponse(BaseResponse):
    """Response dengan pagination"""
    data: List[Any] = []
    pagination: Optional[PaginationMeta] = None
