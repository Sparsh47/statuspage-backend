import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
import json

from core.auth import verify_clerk_token
from db.session import get_db
from models.service import Service, ServiceStatusUpdate
from schemas.service import (
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
    ServiceStatusHistoryResponse,
)
from core.redis_client import redis_client

router = APIRouter(prefix="/services", tags=["services"])

# Helper to convert SQLAlchemy model to dict

def service_to_dict(service: Service) -> dict:
    return {
        "id": str(service.id),
        "name": service.name,
        "description": service.description,
        "organization_id": service.organization_id,
        "current_status": service.current_status,
        "created_at": service.created_at,
        "updated_at": service.updated_at or datetime.utcnow(),
    }

@router.get("/", response_model=list[ServiceResponse])
def list_services(
        db: Session = Depends(get_db),
        token_payload: Dict[str, Any] = Depends(verify_clerk_token),
):
    org_id = token_payload.get("org_id")
    services = db.query(Service).filter(Service.organization_id == org_id).all()
    return [ServiceResponse.model_validate(service_to_dict(s)) for s in services]

@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
        service_in: ServiceCreate,
        db: Session = Depends(get_db),
        token_payload: Dict[str, Any] = Depends(verify_clerk_token),
):
    org_id = token_payload.get("org_id")
    user_id = token_payload.get("user_id")
    service = Service(
        name=service_in.name,
        description=service_in.description,
        organization_id=org_id,
        current_status=service_in.current_status,
    )
    db.add(service)
    db.commit()
    db.refresh(service)

    # initial status record
    status_record = ServiceStatusUpdate(
        service_id=service.id,
        status=service.current_status,
        created_by=user_id,
    )
    db.add(status_record)
    db.commit()

    # Publish via Redis
    event = {
        "type": "service",
        "id": str(service.id),
        "name": service.name,
        "current_status": service.current_status,
        "updated_at": datetime.utcnow().isoformat(),
    }
    await redis_client.publish("status_updates", json.dumps(event))

    return ServiceResponse.model_validate(service_to_dict(service))

@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(
        service_id: int,
        db: Session = Depends(get_db),
        token_payload: Dict[str, Any] = Depends(verify_clerk_token),
):
    org_id = token_payload.get("org_id")
    service = (
        db.query(Service)
        .filter(Service.id == service_id, Service.organization_id == org_id)
        .first()
    )
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return ServiceResponse.model_validate(service_to_dict(service))

@router.patch("/{service_id}", response_model=ServiceResponse)
async def update_service(
        service_id: int,
        service_in: ServiceUpdate,
        db: Session = Depends(get_db),
        token_payload: Dict[str, Any] = Depends(verify_clerk_token),
):
    org_id = token_payload.get("org_id")
    user_id = token_payload.get("user_id")
    service = (
        db.query(Service)
        .filter(Service.id == service_id, Service.organization_id == org_id)
        .first()
    )
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # If status changed, record history
    if service_in.current_status and service_in.current_status != service.current_status:
        status_record = ServiceStatusUpdate(
            service_id=service.id,
            status=service_in.current_status,
            created_by=user_id,
        )
        db.add(status_record)

    # apply other updates
    for field, value in service_in.dict(exclude_unset=True).items():
        setattr(service, field, value)

    db.commit()
    db.refresh(service)

    # Publish update
    event = {
        "type": "service",
        "id": str(service.id),
        "current_status": service.current_status,
        "updated_at": service.updated_at.isoformat(),
    }
    await redis_client.publish("status_updates", json.dumps(event))

    return ServiceResponse.model_validate(service_to_dict(service))

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
        service_id: int,
        db: Session = Depends(get_db),
        token_payload: Dict[str, Any] = Depends(verify_clerk_token),
):
    org_id = token_payload.get("org_id")
    service = (
        db.query(Service)
        .filter(Service.id == service_id, Service.organization_id == org_id)
        .first()
    )
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(service)
    db.commit()

@router.get("/{service_id}/history", response_model=list[ServiceStatusHistoryResponse])
def service_history(
        service_id: int,
        db: Session = Depends(get_db),
        token_payload: Dict[str, Any] = Depends(verify_clerk_token),
):
    org_id = token_payload.get("org_id")
    service = (
        db.query(Service)
        .filter(Service.id == service_id, Service.organization_id == org_id)
        .first()
    )
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return [
        ServiceStatusHistoryResponse.model_validate({
            "id": str(su.id),
            "status": su.status,
            "created_at": su.created_at,
            "updated_at": su.updated_at or su.created_at,
            "created_by": su.created_by,
            "service_id": str(su.service_id),
        })
        for su in service.status_updates
    ]