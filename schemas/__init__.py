from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

class BaseResponse (BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True