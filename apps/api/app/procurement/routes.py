from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.procurement.models import Approval, Bid, Contract, PurchaseOrder, PurchaseOrderItem, RFQ, RFQItem
from app.procurement.schemas import BidCreate, ContractCreate, DecisionInput, PurchaseOrderCreate, RFQCreate
from app.tenant import get_tenant_record, require_roles, tenant_user
from app.vendors.models import Vendor

router = APIRouter(tags=["procurement"])


def tenant_record(model, record_id: str, user: User, db: Session):
    return get_tenant_record(model, record_id, user.organization_id, db)


def assert_vendor(vendor_id: str, user: User, db: Session) -> Vendor:
    return tenant_record(Vendor, vendor_id, user, db)


def next_number(model, field, prefix: str, user: User, db: Session) -> str:
    count = db.scalar(select(func.count(model.id)).where(model.organization_id == user.organization_id)) or 0
    return f"{prefix}-{date.today().year}-{count + 1:04d}"


@router.get("/rfqs")
def list_rfqs(user: User = Depends(require_roles("procurement_manager", "finance_manager", "auditor", "viewer")), db: Session = Depends(get_db)):
    rows = db.scalars(select(RFQ).where(RFQ.organization_id == user.organization_id).order_by(RFQ.created_at.desc())).all()
    result = []
    for rfq in rows:
        bid_count = db.scalar(select(func.count(Bid.id)).where(Bid.rfq_id == rfq.id, Bid.organization_id == user.organization_id)) or 0
        result.append({**{key: value for key, value in rfq.__dict__.items() if not key.startswith("_")}, "bid_count": bid_count})
    return result


@router.post("/rfqs", status_code=status.HTTP_201_CREATED)
def create_rfq(payload: RFQCreate, user: User = Depends(require_roles("procurement_manager")), db: Session = Depends(get_db)):
    if payload.deadline < date.today():
        raise HTTPException(status_code=422, detail="The submission deadline must be today or later")
    rfq = RFQ(organization_id=user.organization_id, created_by=user.id, rfq_number=next_number(RFQ, RFQ.rfq_number, "RFQ", user, db), **payload.model_dump(exclude={"items"}))
    db.add(rfq)
    db.flush()
    for item in payload.items:
        db.add(RFQItem(rfq_id=rfq.id, organization_id=user.organization_id, created_by=user.id, **item.model_dump()))
    db.commit()
    db.refresh(rfq)
    return {**{key: value for key, value in rfq.__dict__.items() if not key.startswith("_")}, "bid_count": 0, "items": payload.items}


@router.get("/rfqs/{rfq_id}")
def get_rfq(rfq_id: str, user: User = Depends(require_roles("procurement_manager", "finance_manager", "auditor", "viewer")), db: Session = Depends(get_db)):
    rfq = tenant_record(RFQ, rfq_id, user, db)
    items = db.scalars(select(RFQItem).where(RFQItem.rfq_id == rfq.id, RFQItem.organization_id == user.organization_id)).all()
    bids = db.scalars(select(Bid).where(Bid.rfq_id == rfq.id, Bid.organization_id == user.organization_id)).all()
    return {"rfq": rfq, "items": items, "bids": bids}


@router.post("/rfqs/{rfq_id}/publish")
def request_rfq_publication(rfq_id: str, user: User = Depends(require_roles("procurement_manager")), db: Session = Depends(get_db)):
    rfq = tenant_record(RFQ, rfq_id, user, db)
    if rfq.status not in {"draft", "rejected"}:
        raise HTTPException(status_code=409, detail="Only a draft RFQ can be sent for approval")
    rfq.status = "pending_approval"
    db.add(Approval(organization_id=user.organization_id, created_by=user.id, requested_by=user.id, object_type="rfq", object_id=rfq.id, title=f"Publish {rfq.rfq_number}: {rfq.title}"))
    db.commit()
    db.refresh(rfq)
    return rfq


@router.post("/rfqs/{rfq_id}/bids", status_code=status.HTTP_201_CREATED)
def submit_bid(rfq_id: str, payload: BidCreate, user: User = Depends(require_roles("procurement_manager", "vendor_manager")), db: Session = Depends(get_db)):
    rfq = tenant_record(RFQ, rfq_id, user, db)
    vendor = assert_vendor(payload.vendor_id, user, db)
    if rfq.status != "open":
        raise HTTPException(status_code=409, detail="This RFQ is not open for bids")
    if rfq.deadline < date.today():
        raise HTTPException(status_code=409, detail="The RFQ submission deadline has passed")
    if vendor.status != "active" or vendor.verification_status != "verified":
        raise HTTPException(status_code=409, detail="Only active, verified vendors can submit bids")
    bid = Bid(organization_id=user.organization_id, created_by=user.id, rfq_id=rfq.id, **payload.model_dump())
    db.add(bid)
    db.commit()
    db.refresh(bid)
    return {"id": bid.id, "rfq_id": bid.rfq_id, "vendor_id": bid.vendor_id, "vendor_name": vendor.name, "amount": bid.amount, "technical_score": bid.technical_score, "delivery_days": bid.delivery_days, "warranty_months": bid.warranty_months, "proposal": bid.proposal, "status": bid.status, "created_at": bid.created_at}


@router.get("/bids")
def list_bids(rfq_id: str | None = None, user: User = Depends(require_roles("procurement_manager", "vendor_manager", "auditor", "viewer")), db: Session = Depends(get_db)):
    query = select(Bid).where(Bid.organization_id == user.organization_id)
    if rfq_id:
        query = query.where(Bid.rfq_id == rfq_id)
    bids = db.scalars(query.order_by(Bid.created_at.desc())).all()
    result = []
    for bid in bids:
        vendor = tenant_record(Vendor, bid.vendor_id, user, db)
        result.append({"id": bid.id, "rfq_id": bid.rfq_id, "rfq_number": tenant_record(RFQ, bid.rfq_id, user, db).rfq_number, "vendor_id": bid.vendor_id, "vendor_name": vendor.name, "amount": bid.amount, "technical_score": bid.technical_score, "delivery_days": bid.delivery_days, "warranty_months": bid.warranty_months, "vendor_trust_score": vendor.trust_score, "vendor_risk_level": vendor.risk_level, "status": bid.status, "created_at": bid.created_at})
    return result


@router.post("/bids/{bid_id}/decision")
def decide_bid(bid_id: str, payload: DecisionInput, user: User = Depends(require_roles("procurement_manager")), db: Session = Depends(get_db)):
    bid = tenant_record(Bid, bid_id, user, db)
    if payload.decision not in {"award", "decline"}:
        raise HTTPException(status_code=422, detail="Choose award or decline for a bid")
    rfq = tenant_record(RFQ, bid.rfq_id, user, db)
    if bid.status != "submitted" or rfq.status not in {"open", "evaluation"}:
        raise HTTPException(status_code=409, detail="This bid cannot be decided in its current state")
    if payload.decision == "award":
        bid.status = "awarded"
        rfq.status = "awarded"
        other_bids = db.scalars(select(Bid).where(Bid.rfq_id == rfq.id, Bid.id != bid.id, Bid.organization_id == user.organization_id)).all()
        for other in other_bids:
            other.status = "declined"
    else:
        bid.status = "declined"
    db.commit()
    return {"id": bid.id, "status": bid.status, "rfq_status": rfq.status}


@router.get("/approvals")
def list_approvals(user: User = Depends(require_roles("procurement_manager", "finance_manager", "auditor")), db: Session = Depends(get_db)):
    return db.scalars(select(Approval).where(Approval.organization_id == user.organization_id).order_by(Approval.created_at.desc())).all()


@router.post("/approvals/{approval_id}/decision")
def decide_approval(approval_id: str, payload: DecisionInput, user: User = Depends(require_roles("procurement_manager", "finance_manager")), db: Session = Depends(get_db)):
    approval = tenant_record(Approval, approval_id, user, db)
    if payload.decision not in {"approve", "reject"}:
        raise HTTPException(status_code=422, detail="Choose approve or reject for an approval")
    if approval.status != "pending":
        raise HTTPException(status_code=409, detail="This approval has already been resolved")
    approved = payload.decision == "approve"
    approval.status = "approved" if approved else "rejected"
    approval.comment = payload.comment
    if approval.object_type == "rfq":
        record = tenant_record(RFQ, approval.object_id, user, db)
        record.status = "open" if approved else "rejected"
    elif approval.object_type == "contract":
        record = tenant_record(Contract, approval.object_id, user, db)
        record.status = "active" if approved else "rejected"
    elif approval.object_type == "purchase_order":
        record = tenant_record(PurchaseOrder, approval.object_id, user, db)
        record.status = "approved" if approved else "rejected"
    db.commit()
    return approval


@router.get("/contracts")
def list_contracts(user: User = Depends(require_roles("procurement_manager", "finance_manager", "auditor", "viewer")), db: Session = Depends(get_db)):
    rows = db.scalars(select(Contract).where(Contract.organization_id == user.organization_id).order_by(Contract.created_at.desc())).all()
    return [{**{key: value for key, value in row.__dict__.items() if not key.startswith("_")}, "vendor_name": tenant_record(Vendor, row.vendor_id, user, db).name} for row in rows]


@router.post("/contracts", status_code=status.HTTP_201_CREATED)
def create_contract(payload: ContractCreate, user: User = Depends(require_roles("procurement_manager")), db: Session = Depends(get_db)):
    vendor = assert_vendor(payload.vendor_id, user, db)
    if payload.end_date < payload.start_date:
        raise HTTPException(status_code=422, detail="The contract end date must be after its start date")
    if payload.rfq_id:
        tenant_record(RFQ, payload.rfq_id, user, db)
    if payload.bid_id:
        bid = tenant_record(Bid, payload.bid_id, user, db)
        if bid.vendor_id != vendor.id or bid.status != "awarded":
            raise HTTPException(status_code=409, detail="A linked bid must be awarded to the selected vendor")
    contract = Contract(organization_id=user.organization_id, created_by=user.id, contract_number=next_number(Contract, Contract.contract_number, "CTR", user, db), status="pending_approval", **payload.model_dump())
    db.add(contract)
    db.flush()
    db.add(Approval(organization_id=user.organization_id, created_by=user.id, requested_by=user.id, object_type="contract", object_id=contract.id, title=f"Contract review: {contract.title}"))
    db.commit()
    db.refresh(contract)
    return {**{key: value for key, value in contract.__dict__.items() if not key.startswith("_")}, "vendor_name": vendor.name}


@router.get("/purchase-orders")
def list_purchase_orders(user: User = Depends(require_roles("procurement_manager", "finance_manager", "auditor", "viewer")), db: Session = Depends(get_db)):
    rows = db.scalars(select(PurchaseOrder).where(PurchaseOrder.organization_id == user.organization_id).order_by(PurchaseOrder.created_at.desc())).all()
    return [{**{key: value for key, value in row.__dict__.items() if not key.startswith("_")}, "vendor_name": tenant_record(Vendor, row.vendor_id, user, db).name, "item_count": db.scalar(select(func.count(PurchaseOrderItem.id)).where(PurchaseOrderItem.purchase_order_id == row.id, PurchaseOrderItem.organization_id == user.organization_id)) or 0} for row in rows]


@router.post("/purchase-orders", status_code=status.HTTP_201_CREATED)
def create_purchase_order(payload: PurchaseOrderCreate, user: User = Depends(require_roles("procurement_manager")), db: Session = Depends(get_db)):
    vendor = assert_vendor(payload.vendor_id, user, db)
    if payload.rfq_id:
        tenant_record(RFQ, payload.rfq_id, user, db)
    if payload.contract_id:
        contract = tenant_record(Contract, payload.contract_id, user, db)
        if contract.vendor_id != vendor.id or contract.status != "active":
            raise HTTPException(status_code=409, detail="A purchase order requires an active contract with the same vendor")
    data = payload.model_dump(exclude={"items"})
    if payload.items:
        calculated_total = sum(item.quantity * item.unit_price for item in payload.items)
        if abs(calculated_total - payload.amount) > 0.01:
            raise HTTPException(status_code=422, detail="The order amount must equal the sum of its line items")
    order = PurchaseOrder(organization_id=user.organization_id, created_by=user.id, po_number=next_number(PurchaseOrder, PurchaseOrder.po_number, "PO", user, db), status="pending_approval", **data)
    db.add(order)
    db.flush()
    for item in payload.items:
        db.add(PurchaseOrderItem(purchase_order_id=order.id, organization_id=user.organization_id, created_by=user.id, **item.model_dump()))
    db.add(Approval(organization_id=user.organization_id, created_by=user.id, requested_by=user.id, object_type="purchase_order", object_id=order.id, title=f"Purchase order approval: {order.title}"))
    db.commit()
    db.refresh(order)
    return {**{key: value for key, value in order.__dict__.items() if not key.startswith("_")}, "vendor_name": vendor.name, "item_count": len(payload.items)}
