# app/api/routes/organization.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from slugify import slugify
from uuid import uuid4

from models.organization import Organization
from models.service import Service
from models.incident import Incident
from schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
    OrganizationWithDetails,
)
from db.session import get_db

router = APIRouter(
    prefix="/organizations",
    tags=["organizations"]
)

def generate_unique_slug(base_slug: str, db: Session):
    slug = base_slug
    counter = 1
    while db.query(Organization).filter(Organization.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug

@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
        payload: OrganizationCreate,
        db: Session = Depends(get_db)
):
    base_slug = slugify(payload.name)
    payload.slug = generate_unique_slug(base_slug, db)

    org = Organization(**payload.dict())
    db.add(org)
    db.commit()
    db.refresh(org)
    return OrganizationResponse(
        id=str(org.id),
        name=org.name,
        slug=org.slug,
        created_at=org.created_at,
        updated_at=org.updated_at,
        is_active=org.is_active
    )

@router.get("/", response_model=List[OrganizationResponse])
def list_organizations(db: Session = Depends(get_db)):
    return db.query(Organization).all()

@router.get("/{org_id}", response_model=OrganizationWithDetails)
def get_organization(org_id: int, db: Session = Depends(get_db)):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Count services belonging to this org
    services_count = db.query(Service).filter(Service.organization_id == org_id).count()

    # Count active incidents (status != "resolved") for this org
    active_incidents_count = (
        db.query(Incident)
        .filter(
            Incident.organization_id == org_id,
            Incident.status != "resolved"
        )
        .count()
    )

    return OrganizationWithDetails(
        id=org.id,
        name=org.name,
        slug=org.slug,
        created_at=org.created_at,
        updated_at=org.updated_at,
        is_active=org.is_active,
        services_count=services_count,
        active_incidents_count=active_incidents_count,
    )

@router.patch("/{org_id}", response_model=OrganizationResponse)
def update_organization(
        org_id: int,
        payload: OrganizationUpdate,
        db: Session = Depends(get_db)
):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    update_data = payload.dict(exclude_unset=True)

    # If name is changed, update slug too
    if "name" in update_data:
        base_slug = slugify(update_data["name"])
        new_slug = generate_unique_slug(base_slug, db)
        update_data["slug"] = new_slug

    for field, value in update_data.items():
        setattr(org, field, value)

    db.commit()
    db.refresh(org)
    return org

@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(org_id: int, db: Session = Depends(get_db)):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    db.delete(org)
    db.commit()
