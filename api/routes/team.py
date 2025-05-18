# app/api/routes/team.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models.team import Team
from schemas.team import TeamCreate, TeamResponse, TeamUpdate, TeamWithMembers
from schemas.user import UserResponse
from schemas import BaseResponse
from db.session import get_db

router = APIRouter(
    prefix="/organizations/{org_id}/teams",
    tags=["teams"]
)

@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
        org_id: int,
        payload: TeamCreate,
        db: Session = Depends(get_db)
):
    # ensure the organization exists
    from models.organization import Organization
    if not db.get(Organization, org_id):
        raise HTTPException(status_code=404, detail="Organization not found")
    team = Team(**payload.dict())
    db.add(team)
    db.commit()
    db.refresh(team)
    return team

@router.get("/", response_model=List[TeamResponse])
def list_teams(org_id: int, db: Session = Depends(get_db)):
    return db.query(Team).filter(Team.organization_id == org_id).all()

@router.get("/{team_id}", response_model=TeamWithMembers)
def get_team(org_id: int, team_id: int, db: Session = Depends(get_db)):
    team = (
        db.query(Team)
        .filter(Team.id == team_id, Team.organization_id == org_id)
        .first()
    )
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.patch("/{team_id}", response_model=TeamResponse)
def update_team(
        org_id: int,
        team_id: int,
        payload: TeamUpdate,
        db: Session = Depends(get_db)
):
    team = (
        db.query(Team)
        .filter(Team.id == team_id, Team.organization_id == org_id)
        .first()
    )
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(team, field, value)
    db.commit()
    db.refresh(team)
    return team

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(org_id: int, team_id: int, db: Session = Depends(get_db)):
    team = (
        db.query(Team)
        .filter(Team.id == team_id, Team.organization_id == org_id)
        .first()
    )
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    db.delete(team)
    db.commit()
