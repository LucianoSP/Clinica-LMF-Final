from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel
from datetime import date, datetime
from ..utils.date_utils import DateEncoder
import json

T = TypeVar('T')

class StandardResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None

    def json(self, **kwargs):
        return json.dumps(self.dict(), cls=DateEncoder, **kwargs)

class PaginatedResponse(StandardResponse, Generic[T]):
    items: List[T]
    total: int
    page: int
    total_pages: int
    has_more: bool