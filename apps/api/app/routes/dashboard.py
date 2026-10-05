from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import current_user
from app.models import User
from app.procurement.models import Approval, PurchaseOrder
from app.tenant import tenant_user
from app.operations import OperationRecord
from app.vendors.models import Vendor

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/summary")
def dashboard_summary(user: User = Depends(tenant_user), db: Session = Depends(get_db)):
    org = user.organization_id
    count = lambda model, *filters: db.scalar(select(func.count(model.id)).where(model.organization_id == org, *filters)) or 0
    vendors = count(Vendor)
    verified = count(Vendor, Vendor.verification_status == "verified")
    average_trust = db.scalar(select(func.avg(Vendor.trust_score)).where(Vendor.organization_id == org)) or 0
    orders = count(PurchaseOrder, PurchaseOrder.status.in_(["approved", "pending_approval"]))
    shipments = count(OperationRecord, OperationRecord.record_type == "shipments", OperationRecord.status.in_(["open", "in_transit", "delayed"]))
    delayed = count(OperationRecord, OperationRecord.record_type == "shipments", OperationRecord.status == "delayed")
    pending = db.scalars(select(Approval).where(Approval.organization_id == org, Approval.status == "pending").order_by(Approval.created_at.desc()).limit(5)).all()
    pending_count = count(Approval, Approval.status == "pending")
    attention = []
    for approval in pending:
        requester = db.get(User, approval.requested_by)
        attention.append({"title": approval.title, "vendor": requester.email if requester else "Workspace member", "amount": approval.object_type.replace("_", " ").title(), "kind": approval.object_type.replace("_", " ").upper(), "initials": "TF", "color": "blue"})
    activity_rows = []
    models = [(Vendor, "Vendor record", "name"), (PurchaseOrder, "Purchase order", "po_number"), (OperationRecord, "Operations record", "name")]
    for model, label, attr in models:
        query = select(model).where(model.organization_id == org)
        if model is OperationRecord:
            query = query.where(model.record_type == "shipments")
        for row in db.scalars(query.order_by(model.created_at.desc()).limit(8)).all():
            title = getattr(row, attr, label)
            if model is PurchaseOrder:
                title = f"{row.po_number} · {row.title}"
            activity_rows.append({"title": label, "name": str(title), "created_at": row.created_at, "status": getattr(row, "status", "recorded")})
    activity_rows.sort(key=lambda item: item["created_at"], reverse=True)
    activity = []
    for row in activity_rows[:5]:
        elapsed = max(0, int((date.today() - row["created_at"].date()).days))
        activity.append({"icon": "✓", "title": row["title"], "name": row["name"], "time": "Today" if elapsed == 0 else f"{elapsed}d ago", "status": str(row["status"]).replace("_", " ").title(), "tone": "mint"})
    return {
        "trust_score": round(float(average_trust)),
        "approvals_count": pending_count,
        "metrics": [
            {"label": "Total vendors", "value": str(vendors), "change": "workspace total", "detail": "registered suppliers", "icon": "◈", "tone": "mint"},
            {"label": "Verified vendors", "value": str(verified), "change": f"{round(verified * 100 / vendors) if vendors else 0}%", "detail": "of vendor records", "icon": "✓", "tone": "blue"},
            {"label": "Open purchase orders", "value": str(orders), "change": "awaiting or approved", "detail": "tracked in this workspace", "icon": "▤", "tone": "violet"},
            {"label": "In transit", "value": str(shipments), "change": f"{delayed} delayed", "detail": "active shipment records", "icon": "⇢", "tone": "amber"},
        ],
        "approvals": attention,
        "activity": activity,
    }
