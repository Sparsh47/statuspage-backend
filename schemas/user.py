from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from schemas import BaseResponse


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    # For Clerk integration, we'll use their IDs
    clerk_id: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserResponse(BaseResponse, UserBase):
    clerk_id: str


class UserInDB(UserResponse):
    team_memberships: List["TeamMemberResponse"] = []