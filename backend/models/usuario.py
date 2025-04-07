from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    id: str
    nome: str
    email: str
    tipo_usuario: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True 