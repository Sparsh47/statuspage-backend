# File: api/routes/incidents.py

import json
from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException, Path, Body
from sqlalchemy.orm import Session

from models.incident import Incident, IncidentUpdate as IncidentUpdateModel
from schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
    IncidentWithUpdates,
)
from core.redis_client import redis_client
from db.session import get_db

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post(
    "/",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_incident(
        payload: IncidentCreate = Body(...),
        db: Session = Depends(get_db),
):
    """
    Create a new Incident. service_ids is dropped if present.
    No authentication required.
    """
    data = payload.model_dump()
    # Remove service_ids so it doesn't blow up the constructor
    service_ids = data.pop("service_ids", None)

    # Build and persist the Incident
    inc = Incident(**data)
    db.add(inc)
    db.commit()
    db.refresh(inc)

    # TODO: if you need to link to services, handle `service_ids` here

    # Broadcast the new incident event
    event = {
        "event_type": "incident",
        "id": inc.id,
        "title": inc.title,
        "description": inc.description,
        "type": inc.type,
        "status": inc.status,
        "impact": inc.impact,
        "created_at": inc.created_at.isoformat(),
    }
    await redis_client.publish("status_updates", json.dumps(event))

    return inc


@router.get(
    "/",
    response_model=list[IncidentResponse],
)
def list_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).all()


@router.get(
    "/{incident_id}",
    response_model=IncidentWithUpdates,
)
def get_incident(
        incident_id: int = Path(..., gt=0),
        db: Session = Depends(get_db),
):
    inc = db.get(Incident, incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc


@router.put(
    "/{incident_id}",
    response_model=IncidentResponse,
)
async def update_incident(
        payload: IncidentUpdate = Body(...),
        incident_id: int = Path(..., gt=0),
        db: Session = Depends(get_db),
):
    inc = db.get(Incident, incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(inc, field, val)
    inc.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(inc)

    event = {
        "event_type": "incident",
        "id": inc.id,
        "title": inc.title,
        "description": inc.description,
        "type": inc.type,
        "status": inc.status,
        "impact": inc.impact,
        "updated_at": inc.updated_at.isoformat(),
    }
    await redis_client.publish("status_updates", json.dumps(event))

    return inc


@router.delete(
    "/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_incident(
        incident_id: int,
        db: Session = Depends(get_db),
):
    inc = db.get(Incident, incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    db.delete(inc)
    db.commit()


@router.get(
    "/{incident_id}/updates",
    response_model=list[IncidentResponse],
)
def list_incident_updates(
        incident_id: int,
        db: Session = Depends(get_db),
):
    return (
        db.query(IncidentUpdateModel)
        .filter(IncidentUpdateModel.incident_id == incident_id)
        .order_by(IncidentUpdateModel.created_at.desc())
        .all()
    )
