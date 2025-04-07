from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class StorageBase(BaseModel):
    """Modelo base para Storage"""
    nome: str
    url: str
    size: int
    content_type: str
    referencia_id: Optional[UUID] = None
    tipo_referencia: Optional[str] = None

class StorageCreate(StorageBase):
    pass

class StorageUpdate(StorageBase):
    nome: Optional[str] = None
    url: Optional[str] = None
    size: Optional[int] = None
    content_type: Optional[str] = None
    referencia_id: Optional[UUID] = None
    tipo_referencia: Optional[str] = None

class Storage(StorageBase):
    """Modelo para a entidade Storage"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True