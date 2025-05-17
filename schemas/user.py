from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from __init import BaseResponse


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    # For Clerk integration, we'll use their IDs
    id: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserResponse(BaseResponse, UserBase):
    pass


class UserInDB(UserResponse):
    team_memberships: List["TeamMemberResponse"] = []