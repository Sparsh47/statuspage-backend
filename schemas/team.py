from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from schemas import BaseResponse
from schemas.user import UserResponse


class TeamBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    organization_id: int


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)


class TeamResponse(BaseResponse, TeamBase):
    pass


class TeamMemberBase(BaseModel):
    user_id: str
    team_id: str
    role: str = "member"  # Default role


class TeamMemberCreate(TeamMemberBase):
    pass


class TeamMemberUpdate(BaseModel):
    role: Optional[str] = None


class TeamMemberResponse(BaseResponse, TeamMemberBase):
    pass


class TeamWithMembers(TeamResponse):
    members: List[UserResponse] = []