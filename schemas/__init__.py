from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

class BaseResponse (BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True