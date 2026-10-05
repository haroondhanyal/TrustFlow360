from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import current_user
from app.models import User
from app.organization.models import Role

ADMIN_ROLES = {"organization_admin"}
ROLE_PERMISSIONS = {
    "procurement_manager": {"rfqs.manage", "bids.manage", "contracts.manage", "purchase_orders.manage", "vendors.manage"},
    "vendor_manager": {"vendors.manage", "vendors.verify", "trust_passports.manage"},
    "finance_manager": {"purchase_orders.approve"},
    "auditor": {"organization.view", "vendors.view", "procurement.view", "contracts.view"},
    "viewer": {"organization.view", "vendors.view", "procurement.view", "contracts.view"},
}


def tenant_user(user: User = Depends(current_user)) -> User:
    if not user.organization_id:
        raise HTTPException(status_code=403, detail="Set up an organization before using this feature")
    return user


def require_roles(*roles: str):
    def check(user: User = Depends(tenant_user), db: Session = Depends(get_db)) -> User:
        if user.role in ADMIN_ROLES or user.role in roles:
            return user
        custom_role = db.scalar(select(Role).where(Role.organization_id == user.organization_id, Role.key == user.role))
        allowed = set().union(*(ROLE_PERMISSIONS.get(role, set()) for role in roles))
        if not custom_role or not allowed.intersection(custom_role.permissions):
            raise HTTPException(status_code=403, detail="Your role does not have access to this action")
        return user
    return check


def get_tenant_record(model, record_id: str, organization_id: str, db: Session):
    record = db.get(model, record_id)
    if not record or record.organization_id != organization_id:
        raise HTTPException(status_code=404, detail="Record not found")
    return record
