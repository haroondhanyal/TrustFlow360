from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_token
from app.db.session import get_db
from app.dependencies import current_user
from app.models import Organization, User
from app.schemas import OrganizationCreate, OrganizationResponse, OrganizationSessionResponse

router = APIRouter()


@router.post("", response_model=OrganizationSessionResponse, status_code=status.HTTP_201_CREATED)
def create_organization(payload: OrganizationCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.organization_id:
        raise HTTPException(status_code=409, detail="Your account already belongs to an organization")
    if db.scalar(select(Organization.id).where(Organization.slug == payload.slug)):
        raise HTTPException(status_code=409, detail="That workspace URL is already in use")
    organization = Organization(name=payload.name.strip(), workspace_name=payload.workspace_name.strip(), slug=payload.slug, website=payload.website, industry=payload.industry, company_size=payload.size, country=payload.country)
    db.add(organization)
    db.flush()
    user.organization_id = organization.id
    user.role = "organization_admin"
    db.commit()
    db.refresh(organization)
    access_token, _ = create_token(user.id, "access", organization.id)
    return OrganizationSessionResponse(organization=organization, access_token=access_token)


@router.get("/me", response_model=OrganizationResponse)
def read_my_organization(user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not user.organization_id:
        raise HTTPException(status_code=404, detail="No organization is set up for this account")
    organization = db.get(Organization, user.organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization
