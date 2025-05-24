from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from schemas import BaseResponse
from schemas.user import UserResponse

class TeamBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    slug: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    organization_id: int

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    slug: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None

class TeamResponse(BaseResponse, TeamBase):
    model_config = ConfigDict(from_attributes=True)

class TeamMemberBase(BaseModel):
    user_id: int
    team_id: int
    role: str = Field(default="member", min_length=2, max_length=50)

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMemberUpdate(BaseModel):
    role: Optional[str] = None

class TeamMemberResponse(BaseResponse, TeamMemberBase):
    model_config = ConfigDict(from_attributes=True)

class TeamWithMembers(TeamResponse):
    members: List[UserResponse] = []
