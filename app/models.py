from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime


class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str


class QueryRequest(BaseModel):
    query: str
    parameters: Optional[dict] = None


class QueryResponse(BaseModel):
    data: List[dict]
    row_count: int
    execution_time_ms: float


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime


class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    created_at: Optional[datetime] = None


class UserCreate(BaseModel):
    name: str
    email: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class UserRegistrationResponse(BaseModel):
    user: User
    created: bool
    message: str
