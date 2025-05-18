import logging
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import json

from core.auth import verify_clerk_token
from db.session import get_db
from models.incident import Incident, IncidentUpdate
from schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentWithUpdates,
    IncidentUpdateCreate,
    IncidentUpdateResponse,
)
from core.redis_client import redis_client

router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.get("/", response_model=List[IncidentResponse])
def list_incidents(
        db: Session = Depends(get_db),
        token_payload: Dict[str, Any] = Depends(verify_clerk_token),
):
    incidents = db.query(Incident).filter(Incident.organization_id == token_payload.get("org_id")).all()
    return incidents

@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
        payload: IncidentCreate,
        db: Session = Depends(get_db),
        token_payload: Dict[str, Any] = Depends(verify_clerk_token),
):
    incident = Incident(
        title=payload.title,
        description=payload.description,
        type=payload.incident_type,
        status=payload.status,
        organization_id=token_payload.get("org_id"),
        created_by=token_payload.get("user_id"),
        created_at=datetime.utcnow(),
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    # Publish creation event
    event = {
        "type": "incident",
        "id": str(incident.id),
        "service_id": str(incident.service_id),
        "status": incident.status,
        "created_at": incident.created_at.isoformat(),
    }
    await redis_client.publish("status_updates", json.dumps(event))

    return incident

@router.get("/{incident_id}", response_model=IncidentWithUpdates)
def get_incident(
        incident_id: int,
        db: Session = Depends(get_db),
        token_payload: Dict[str, Any] = Depends(verify_clerk_token),
):
    incident = (
        db.query(Incident)
        .filter(
            Incident.id == incident_id,
            Incident.organization_id == token_payload.get("org_id"),
            )
        .first()
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
        incident_id: int,
        payload: IncidentCreate,
        db: Session = Depends(get_db),
        token_payload: Dict[str, Any] = Depends(verify_clerk_token),
):
    incident = (
        db.query(Incident)
        .filter(
            Incident.id == incident_id,
            Incident.organization_id == token_payload.get("org_id"),
            )
        .first()
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    # Update fields
    for field, value in payload.dict(exclude_unset=True).items():
        if field == "incident_type":
            setattr(incident, "type", value)
        else:
            setattr(incident, field, value)
    incident.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(incident)

    # Publish update event
    event = {
        "type": "incident",
        "id": str(incident.id),
        "service_id": str(incident.service_id),
        "status": incident.status,
        "updated_at": incident.updated_at.isoformat(),
    }
    await redis_client.publish("status_updates", json.dumps(event))

    return incident

@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(
        incident_id: int,
        db: Session = Depends(get_db),
        token_payload: Dict[str, Any] = Depends(verify_clerk_token),
):
    incident = (
        db.query(Incident)
        .filter(
            Incident.id == incident_id,
            Incident.organization_id == token_payload.get("org_id"),
            )
        .first()
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    db.delete(incident)
    db.commit()

@router.post("/{incident_id}/updates", response_model=IncidentUpdateResponse, status_code=status.HTTP_201_CREATED)
async def add_incident_update(
        incident_id: int,
        payload: IncidentUpdateCreate,
        db: Session = Depends(get_db),
        token_payload: Dict[str, Any] = Depends(verify_clerk_token),
):
    update = IncidentUpdate(
        incident_id=incident_id,
        message=payload.message,
        status=payload.status,
        created_by=token_payload.get("user_id"),
        created_at=datetime.utcnow(),
    )
    db.add(update)
    db.commit()
    db.refresh(update)

    # Publish update event
    event = {
        "type": "incident_update",
        "incident_id": str(incident_id),
        "update_id": str(update.id),
        "status": update.status,
        "message": update.message,
        "created_at": update.created_at.isoformat(),
    }
    await redis_client.publish("status_updates", json.dumps(event))

    return update