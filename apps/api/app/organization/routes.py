from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import fingerprint, hash_password
from app.db.session import get_db
from app.models import User
from app.organization.models import Department, Invitation, Role
from app.organization.schemas import DepartmentInput, DepartmentOut, InvitationAccept, InvitationInput, RoleInput, UserOut, UserRoleUpdate
from app.tenant import require_roles, tenant_user

router = APIRouter(prefix="/organization", tags=["organization"])

DEFAULT_ROLES = [
    {"key": "organization_admin", "name": "Organization Admin", "permissions": ["organization.manage", "users.manage", "vendors.manage", "procurement.manage", "contracts.manage"]},
    {"key": "procurement_manager", "name": "Procurement Manager", "permissions": ["vendors.view", "rfqs.manage", "bids.manage", "contracts.manage", "purchase_orders.manage"]},
    {"key": "vendor_manager", "name": "Vendor Manager", "permissions": ["vendors.manage", "trust_passports.view"]},
    {"key": "finance_manager", "name": "Finance Manager", "permissions": ["purchase_orders.view", "purchase_orders.approve"]},
    {"key": "auditor", "name": "Auditor", "permissions": ["organization.view", "vendors.view", "procurement.view", "contracts.view"]},
    {"key": "viewer", "name": "Viewer", "permissions": ["organization.view", "vendors.view", "procurement.view", "contracts.view"]},
]


@router.get("/users", response_model=list[UserOut])
def list_users(user: User = Depends(require_roles("organization_admin")), db: Session = Depends(get_db)):
    return db.scalars(select(User).where(User.organization_id == user.organization_id).order_by(User.created_at.desc())).all()


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(user_id: str, payload: UserRoleUpdate, user: User = Depends(require_roles("organization_admin")), db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target or target.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == user.id:
        raise HTTPException(status_code=400, detail="Ask another administrator to change your own role")
    if payload.department_id:
        department = db.get(Department, payload.department_id)
        if not department or department.organization_id != user.organization_id:
            raise HTTPException(status_code=404, detail="Department not found")
    supported_roles = {role["key"] for role in DEFAULT_ROLES}
    custom_role = db.scalar(select(Role).where(Role.organization_id == user.organization_id, Role.key == payload.role))
    if payload.role not in supported_roles and not custom_role:
        raise HTTPException(status_code=422, detail="Choose an available role")
    target.role = payload.role
    target.department_id = payload.department_id
    db.commit()
    db.refresh(target)
    return target


@router.get("/departments", response_model=list[DepartmentOut])
def list_departments(user: User = Depends(tenant_user), db: Session = Depends(get_db)):
    return db.scalars(select(Department).where(Department.organization_id == user.organization_id).order_by(Department.name)).all()


@router.post("/departments", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
def create_department(payload: DepartmentInput, user: User = Depends(require_roles("organization_admin")), db: Session = Depends(get_db)):
    existing = db.scalar(select(Department).where(Department.organization_id == user.organization_id, Department.name == payload.name))
    if existing:
        raise HTTPException(status_code=409, detail="That department already exists")
    department = Department(organization_id=user.organization_id, created_by=user.id, **payload.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


@router.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(department_id: str, user: User = Depends(require_roles("organization_admin")), db: Session = Depends(get_db)):
    department = db.get(Department, department_id)
    if not department or department.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Department not found")
    db.query(User).filter(User.department_id == department.id, User.organization_id == user.organization_id).update({User.department_id: None})
    db.delete(department)
    db.commit()


@router.get("/roles")
def list_roles(user: User = Depends(tenant_user), db: Session = Depends(get_db)):
    custom = db.scalars(select(Role).where(Role.organization_id == user.organization_id)).all()
    return {"roles": DEFAULT_ROLES, "custom_roles": custom, "current_role": user.role}


@router.post("/roles", status_code=status.HTTP_201_CREATED)
def create_role(payload: RoleInput, user: User = Depends(require_roles("organization_admin")), db: Session = Depends(get_db)):
    if db.scalar(select(Role.id).where(Role.organization_id == user.organization_id, Role.key == payload.key)):
        raise HTTPException(status_code=409, detail="That role key already exists")
    role = Role(organization_id=user.organization_id, created_by=user.id, **payload.model_dump())
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.get("/invitations")
def list_invitations(user: User = Depends(require_roles("organization_admin")), db: Session = Depends(get_db)):
    rows = db.scalars(select(Invitation).where(Invitation.organization_id == user.organization_id).order_by(Invitation.created_at.desc())).all()
    return [{"id": row.id, "email": row.email, "role": row.role, "department_id": row.department_id, "expires_at": row.expires_at, "accepted": row.accepted_at is not None} for row in rows]


@router.post("/invitations", status_code=status.HTTP_201_CREATED)
def invite_user(payload: InvitationInput, user: User = Depends(require_roles("organization_admin")), db: Session = Depends(get_db)):
    email = str(payload.email).lower()
    if db.scalar(select(User.id).where(User.email == email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    if payload.department_id:
        department = db.get(Department, payload.department_id)
        if not department or department.organization_id != user.organization_id:
            raise HTTPException(status_code=404, detail="Department not found")
    invite_token = token_urlsafe(32)
    invitation = Invitation(organization_id=user.organization_id, created_by=user.id, email=email, role=payload.role, department_id=payload.department_id, token_hash=fingerprint(invite_token), expires_at=datetime.now(timezone.utc) + timedelta(days=7))
    db.add(invitation)
    db.commit()
    return {"id": invitation.id, "email": email, "role": invitation.role, "expires_at": invitation.expires_at, "invite_token": invite_token}


@router.post("/invitations/accept", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def accept_invitation(payload: InvitationAccept, db: Session = Depends(get_db)):
    invitation = db.scalar(select(Invitation).where(Invitation.token_hash == fingerprint(payload.token)))
    expiry = invitation.expires_at.replace(tzinfo=timezone.utc) if invitation and invitation.expires_at.tzinfo is None else invitation.expires_at if invitation else None
    if not invitation or invitation.accepted_at or expiry < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="This invitation is invalid or has expired")
    if str(payload.email).lower() != invitation.email.lower():
        raise HTTPException(status_code=400, detail="Use the email address this invitation was sent to")
    if db.scalar(select(User.id).where(User.email == invitation.email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    member = User(organization_id=invitation.organization_id, department_id=invitation.department_id, email=invitation.email, first_name=payload.first_name.strip(), last_name=payload.last_name.strip(), password_hash=hash_password(payload.password), role=invitation.role)
    invitation.accepted_at = datetime.now(timezone.utc)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member
