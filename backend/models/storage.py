from datetime import datetime, date
from typing import Optional, Union
from pydantic import BaseModel
from uuid import UUID
import json


class DateUUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


class StorageBase(BaseModel):
    """Modelo base para Storage"""

    nome: str
    url: str
    size: int
    content_type: str
    created_by: UUID
    updated_by: UUID

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            date: lambda v: v.isoformat() if isinstance(v, date) else v,
            datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v,
            UUID: lambda v: str(v) if isinstance(v, UUID) else v
        }
    }


class StorageCreate(StorageBase):
    """Modelo para criação de Storage"""

    model_config = {
        "json_schema_extra": {
            "example": {
                "nome": "documento.pdf",
                "content_type": "application/pdf",
                "size": 1024,
                "url": "https://example.com/documento.pdf",
                "created_by": "00000000-0000-0000-0000-000000000000",
                "updated_by": "00000000-0000-0000-0000-000000000000",
            }
        }
    }


class StorageUpdate(BaseModel):
    """Modelo para atualização de Storage"""

    nome: Optional[str] = None
    url: Optional[str] = None
    size: Optional[int] = None
    content_type: Optional[str] = None
    updated_by: UUID

    model_config = {
        "json_encoders": {
            UUID: lambda v: str(v) if isinstance(v, UUID) else v
        }
    }


class Storage(BaseModel):
    """Modelo completo de Storage"""

    id: str
    nome: Optional[str] = None
    url: Optional[str] = None
    size: Optional[int] = None
    content_type: Optional[str] = None
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_at: Optional[Union[datetime, str]] = None

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            date: lambda v: v.isoformat() if isinstance(v, date) else v,
            datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v,
            UUID: lambda v: str(v) if isinstance(v, UUID) else v
        }
    }
