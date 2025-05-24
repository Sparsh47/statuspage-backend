# app/api/routes/organization.py
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session, selectinload
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

@router.post(
    "/",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
        payload: OrganizationCreate,
        db: Session = Depends(get_db),
):
    org = Organization(**payload.dict())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

@router.get("/", response_model=List[OrganizationResponse])
def list_organizations(db: Session = Depends(get_db)):
    return db.query(Organization).all()

@router.get(
    "/{org_id}",
    response_model=OrganizationWithDetails,
)
def get_organization(
        org_id: int = Path(..., gt=0),
        db: Session = Depends(get_db),
):
    org = (
        db.query(Organization)
        .options(selectinload(Organization.teams))
        .filter(Organization.id == org_id)
        .first()
    )
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with id={org_id} not found",
        )
    return org


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
