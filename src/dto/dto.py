from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: Optional[str]
    data: Optional[T]


class CreateUserDto(BaseModel):
    name: str
    email: str
    password: str
    secret: str  # 생성시 필요한 비밀키
