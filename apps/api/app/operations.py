"""Phase 4 tenant-scoped operational records and local verification utilities."""
from datetime import date
import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import JSON, ForeignKey, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.db.base import Base, TenantRecord
from app.db.session import get_db
from app.models import User
from app.tenant import require_roles


class OperationRecord(TenantRecord, Base):
    __tablename__ = "operation_records"
    record_type: Mapped[str] = mapped_column(String(40), index=True)
    name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(40), default="open")
    data: Mapped[dict] = mapped_column(JSON, default=dict)


class ProofRecord(TenantRecord, Base):
    __tablename__ = "proof_records"
    subject_type: Mapped[str] = mapped_column(String(40))
    subject_id: Mapped[str] = mapped_column(String(36), index=True)
    digest: Mapped[str] = mapped_column(String(64), unique=True)
    previous_digest: Mapped[str | None] = mapped_column(String(64))
    statement: Mapped[dict] = mapped_column(JSON)


router = APIRouter(tags=["operations"])
special_router = APIRouter(tags=["operations"])
READ_ROLES = ("organization_admin", "procurement_manager", "finance_manager", "vendor_manager", "auditor", "viewer")
WRITE_ROLES = ("organization_admin", "procurement_manager", "finance_manager", "vendor_manager")
KINDS = {"shipments", "finance", "risks", "credentials", "assets"}


class RecordInput(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    status: str = Field(default="open", max_length=40)
    data: dict = Field(default_factory=dict)


class DecisionInput(BaseModel):
    decision: str


def serialize(row):
    return {"id": row.id, "name": row.name, "status": row.status, **(row.data or {}), "created_at": row.created_at}


@router.get("/{kind}")
def list_records(kind: str, user: User = Depends(require_roles(*READ_ROLES)), db: Session = Depends(get_db)):
    if kind not in KINDS:
        raise HTTPException(404, "Unknown operations module")
    rows = db.scalars(select(OperationRecord).where(OperationRecord.organization_id == user.organization_id, OperationRecord.record_type == kind).order_by(OperationRecord.created_at.desc())).all()
    return [serialize(row) for row in rows]


@router.post("/{kind}", status_code=201)
def create_record(kind: str, payload: RecordInput, user: User = Depends(require_roles(*WRITE_ROLES)), db: Session = Depends(get_db)):
    if kind not in KINDS:
        raise HTTPException(404, "Unknown operations module")
    row = OperationRecord(organization_id=user.organization_id, created_by=user.id, record_type=kind, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize(row)


@router.post("/{kind}/{record_id}/decision")
def decide_record(kind: str, record_id: str, payload: DecisionInput, user: User = Depends(require_roles(*WRITE_ROLES)), db: Session = Depends(get_db)):
    row = db.scalar(select(OperationRecord).where(OperationRecord.id == record_id, OperationRecord.organization_id == user.organization_id, OperationRecord.record_type == kind))
    if not row:
        raise HTTPException(404, "Record not found")
    allowed = {"shipments": {"in_transit", "delivered", "delayed"}, "finance": {"paid", "overdue", "approved"}, "risks": {"mitigated", "accepted", "open"}, "credentials": {"verified", "revoked"}, "assets": {"active", "retired"}}
    if payload.decision not in allowed.get(kind, set()):
        raise HTTPException(422, "Decision is not valid for this record")
    row.status = payload.decision
    db.commit()
    return serialize(row)


@special_router.post("/proofs/{kind}/{record_id}", status_code=201)
def create_proof(kind: str, record_id: str, user: User = Depends(require_roles(*WRITE_ROLES)), db: Session = Depends(get_db)):
    if kind not in KINDS:
        raise HTTPException(404, "Unknown record type")
    row = db.scalar(select(OperationRecord).where(OperationRecord.id == record_id, OperationRecord.organization_id == user.organization_id, OperationRecord.record_type == kind))
    if not row:
        raise HTTPException(404, "Record not found")
    previous = db.scalar(select(ProofRecord).where(ProofRecord.organization_id == user.organization_id).order_by(ProofRecord.created_at.desc()))
    statement = {"type": kind, "id": row.id, "name": row.name, "status": row.status, "data": row.data, "created_at": row.created_at.isoformat()}
    raw = json.dumps({"statement": statement, "previous": previous.digest if previous else None}, sort_keys=True, separators=(",", ":"))
    proof = ProofRecord(organization_id=user.organization_id, created_by=user.id, subject_type=kind, subject_id=row.id, statement=statement, previous_digest=previous.digest if previous else None, digest=hashlib.sha256(raw.encode()).hexdigest())
    db.add(proof)
    db.commit()
    return {"id": proof.id, "digest": proof.digest, "previous_digest": proof.previous_digest, "statement": statement, "verification": "local hash-chain proof; not a public blockchain transaction"}


@special_router.get("/proofs")
def list_proofs(user: User = Depends(require_roles(*READ_ROLES)), db: Session = Depends(get_db)):
    rows = db.scalars(select(ProofRecord).where(ProofRecord.organization_id == user.organization_id).order_by(ProofRecord.created_at.desc())).all()
    return [{"id": r.id, "subject_type": r.subject_type, "subject_id": r.subject_id, "digest": r.digest, "previous_digest": r.previous_digest, "created_at": r.created_at, "verification": "local hash-chain"} for r in rows]


@special_router.get("/verify/{digest}")
def verify_proof(digest: str, user: User = Depends(require_roles(*READ_ROLES)), db: Session = Depends(get_db)):
    proof = db.scalar(select(ProofRecord).where(ProofRecord.digest == digest, ProofRecord.organization_id == user.organization_id))
    if not proof:
        raise HTTPException(404, "Proof not found in this workspace")
    raw = json.dumps({"statement": proof.statement, "previous": proof.previous_digest}, sort_keys=True, separators=(",", ":"))
    valid = hashlib.sha256(raw.encode()).hexdigest() == proof.digest
    return {"valid": valid, "digest": proof.digest, "statement": proof.statement, "scope": "organization-local hash chain"}


@special_router.post("/assistant")
def assistant(payload: dict, user: User = Depends(require_roles(*READ_ROLES)), db: Session = Depends(get_db)):
    """Small local rules assistant; no external AI or document service required."""
    question = str(payload.get("question", "")).lower()
    rows = db.scalars(select(OperationRecord).where(OperationRecord.organization_id == user.organization_id)).all()
    if "shipment" in question or "delivery" in question:
        matched = [r for r in rows if r.record_type == "shipments" and r.status not in {"delivered", "cancelled"}]
        answer = f"There are {len(matched)} shipments still in progress." + (" Review: " + ", ".join(r.name for r in matched[:5]) if matched else "")
    elif "risk" in question:
        matched = [r for r in rows if r.record_type == "risks" and r.status == "open"]
        answer = f"There are {len(matched)} open risk items." + (" Highest priority: " + ", ".join(r.name for r in matched[:5]) if matched else "")
    elif "invoice" in question or "finance" in question or "payment" in question:
        matched = [r for r in rows if r.record_type == "finance" and r.status not in {"paid", "closed"}]
        answer = f"There are {len(matched)} finance records awaiting action."
    else:
        answer = f"Your workspace has {len(rows)} operational records. Ask about shipments, risks, invoices or finance for a scoped summary."
    return {"answer": answer, "mode": "local workspace rules", "records_considered": len(rows)}
