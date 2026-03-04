from pydantic import BaseModel
from typing import Optional, Generic, TypeVar

T = TypeVar('T')

class ErrorDetail(BaseModel):
    """Error detail schema cho API responses"""
    code: str
    message: str
    partial_results: Optional[dict] = None

class ApiResponse(BaseModel, Generic[T]):
    """
    Standardized API response envelope.
    
    Ensures consistent response structure across all endpoints:
    - success: boolean indicating operation success
    - data: actual response data (None if error)
    - error: error details (None if success)
    """
    success: bool
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"questions": []},
                "error": None
            }
        }
