# File: api/routes/services.py

import json
from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException, Path, Body
from sqlalchemy.orm import Session

from models.service import Service, ServiceStatusUpdate
from schemas.service import ServiceCreate, ServiceResponse, ServiceUpdate
from core.redis_client import redis_client
from db.session import get_db
from core.auth import verify_clerk_token

router = APIRouter(prefix="/services", tags=["services"])

@router.post(
    "/",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_service(
        service_in: ServiceCreate,
        db: Session = Depends(get_db),
):
    # 1. Derive a slug from the name
    slug_value = service_in.name.strip().lower().replace(" ", "-")

    # 2. Persist the new Service
    svc = Service(
        name=service_in.name,
        slug=slug_value,
        description=service_in.description,
        organization_id=None,
        current_status=service_in.current_status,
    )
    db.add(svc)
    db.commit()
    db.refresh(svc)

    # 3. Record an initial status update WITH timestamps
    now = datetime.utcnow()
    status_record = ServiceStatusUpdate(
        service_id=svc.id,
        status=svc.current_status,
        message=None,
        created_by=None,
        created_at=now,
        updated_at=now,             # ← ensure this is never NULL
    )
    db.add(status_record)
    db.commit()

    # 4. Broadcast via Redis
    event = {
        "event_type": "service",
        "id": svc.id,
        "name": svc.name,
        "slug": svc.slug,
        "current_status": svc.current_status,
        "updated_at": now.isoformat(),
    }
    await redis_client.publish("status_updates", json.dumps(event))

    return svc

@router.get(
    "/",
    response_model=list[ServiceResponse],
)
async def list_services(
        db: Session = Depends(get_db),
        token_payload: dict = Depends(verify_clerk_token),
):
    # No org_id filtering—just return everything
    return db.query(Service).all()


@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
)
async def get_service(
        service_id: int = Path(..., gt=0),
        db: Session = Depends(get_db),
        token_payload: dict = Depends(verify_clerk_token),
):
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.put(
    "/{service_id}",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
)
async def update_service(
        payload: ServiceUpdate = Body(...),
        service_id: int = Path(..., gt=0),
        db: Session = Depends(get_db),
):
    """
    Update an existing Service. Fields in `payload` that are unset will be left intact.
    No authentication required.
    """
    svc = db.get(Service, service_id)
    if not svc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    # Apply only the provided fields
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(svc, field, value)

    svc.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(svc)

    # Broadcast the update event
    event = {
        "event_type": "service",
        "id": svc.id,
        "name": svc.name,
        "slug": svc.slug,
        "current_status": svc.current_status,
        "updated_at": svc.updated_at.isoformat(),
    }
    await redis_client.publish("status_updates", json.dumps(event))

    return svc

@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_service(
        service_id: int,
        db: Session = Depends(get_db),
        token_payload: dict = Depends(verify_clerk_token),
):
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(service)
    db.commit()


@router.post(
    "/{service_id}/status",
    response_model=ServiceResponse,
)
async def create_service_status_update(
        service_id: int,
        payload: ServiceUpdate,
        db: Session = Depends(get_db),
        token_payload: dict = Depends(verify_clerk_token),
):
    user_id = token_payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    status_record = ServiceStatusUpdate(
        service_id=service_id,
        status=payload.current_status,
        created_by=user_id,
    )
    db.add(status_record)

    service = db.get(Service, service_id)
    service.current_status = payload.current_status
    service.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(service)

    event = {
        "event_type": "service",
        "id": service.id,
        "name": service.name,
        "slug": service.slug,
        "current_status": service.current_status,
        "updated_at": service.updated_at.isoformat(),
    }
    await redis_client.publish("status_updates", json.dumps(event))

    return service


@router.get(
    "/{service_id}/status/history",
    response_model=list[ServiceResponse],
)
async def list_service_status_history(
        service_id: int,
        db: Session = Depends(get_db),
        token_payload: dict = Depends(verify_clerk_token),
):
    return (
        db.query(ServiceStatusUpdate)
        .filter(ServiceStatusUpdate.service_id == service_id)
        .order_by(ServiceStatusUpdate.created_at.desc())
        .all()
    )
