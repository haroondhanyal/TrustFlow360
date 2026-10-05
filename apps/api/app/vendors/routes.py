from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import new_id
from app.tenant import get_tenant_record, require_roles, tenant_user
from app.vendors.models import Vendor, VendorCertification
from app.vendors.schemas import CertificationCreate, VendorCreate, VendorOut, VendorUpdate

router = APIRouter(prefix="/vendors", tags=["vendors"])


def vendor_score(vendor: Vendor) -> float:
    return round(float(vendor.compliance_score) * 0.45 + float(vendor.delivery_score) * 0.35 + (100 if vendor.verification_status == "verified" else 45) * 0.20, 1)


@router.get("", response_model=list[VendorOut])
def list_vendors(q: str | None = None, category: str | None = None, risk: str | None = None, status_filter: str | None = Query(default=None, alias="status"), user=Depends(require_roles("vendor_manager", "procurement_manager", "auditor", "viewer")), db: Session = Depends(get_db)):
    query = select(Vendor).where(Vendor.organization_id == user.organization_id)
    if q:
        term = f"%{q.strip()}%"
        query = query.where(or_(Vendor.name.ilike(term), Vendor.vendor_number.ilike(term), Vendor.country.ilike(term)))
    if category:
        query = query.where(Vendor.category == category)
    if risk:
        query = query.where(Vendor.risk_level == risk)
    if status_filter:
        query = query.where(Vendor.status == status_filter)
    return db.scalars(query.order_by(Vendor.created_at.desc())).all()


@router.post("", response_model=VendorOut, status_code=status.HTTP_201_CREATED)
def create_vendor(payload: VendorCreate, user=Depends(require_roles("vendor_manager", "procurement_manager")), db: Session = Depends(get_db)):
    count = db.scalar(select(func.count(Vendor.id)).where(Vendor.organization_id == user.organization_id)) or 0
    vendor = Vendor(organization_id=user.organization_id, created_by=user.id, vendor_number=f"VEN-{count + 1:04d}", **payload.model_dump())
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


@router.get("/{vendor_id}", response_model=VendorOut)
def get_vendor(vendor_id: str, user=Depends(require_roles("vendor_manager", "procurement_manager", "auditor", "viewer")), db: Session = Depends(get_db)):
    return get_tenant_record(Vendor, vendor_id, user.organization_id, db)


@router.patch("/{vendor_id}", response_model=VendorOut)
def update_vendor(vendor_id: str, payload: VendorUpdate, user=Depends(require_roles("vendor_manager", "procurement_manager")), db: Session = Depends(get_db)):
    vendor = get_tenant_record(Vendor, vendor_id, user.organization_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(vendor, field, value)
    db.commit()
    db.refresh(vendor)
    return vendor


@router.post("/{vendor_id}/verify", response_model=VendorOut)
def verify_vendor(vendor_id: str, user=Depends(require_roles("vendor_manager")), db: Session = Depends(get_db)):
    vendor = get_tenant_record(Vendor, vendor_id, user.organization_id, db)
    if vendor.status == "suspended":
        raise HTTPException(status_code=409, detail="A suspended vendor cannot be verified")
    vendor.verification_status = "verified"
    vendor.compliance_score = 95 if vendor.tax_id and vendor.registration_number else 82
    vendor.trust_score = vendor_score(vendor)
    vendor.risk_level = "low" if vendor.trust_score >= 80 else "medium"
    db.commit()
    db.refresh(vendor)
    return vendor


@router.post("/{vendor_id}/suspend", response_model=VendorOut)
def suspend_vendor(vendor_id: str, user=Depends(require_roles("vendor_manager")), db: Session = Depends(get_db)):
    vendor = get_tenant_record(Vendor, vendor_id, user.organization_id, db)
    vendor.status = "suspended"
    vendor.risk_level = "high"
    db.commit()
    db.refresh(vendor)
    return vendor


@router.get("/{vendor_id}/passport")
def vendor_passport(vendor_id: str, user=Depends(require_roles("vendor_manager", "procurement_manager", "auditor", "viewer")), db: Session = Depends(get_db)):
    vendor = get_tenant_record(Vendor, vendor_id, user.organization_id, db)
    certificates = db.scalars(select(VendorCertification).where(VendorCertification.vendor_id == vendor.id, VendorCertification.organization_id == user.organization_id)).all()
    return {"vendor": VendorOut.model_validate(vendor), "certifications": certificates, "trust_score": vendor.trust_score, "verification_status": vendor.verification_status, "risk_level": vendor.risk_level, "verified_certifications": sum(c.verified for c in certificates), "blockchain_proof": "not_recorded"}


@router.post("/{vendor_id}/certifications", status_code=status.HTTP_201_CREATED)
def add_certification(vendor_id: str, payload: CertificationCreate, user=Depends(require_roles("vendor_manager")), db: Session = Depends(get_db)):
    vendor = get_tenant_record(Vendor, vendor_id, user.organization_id, db)
    certification = VendorCertification(vendor_id=vendor.id, organization_id=user.organization_id, created_by=user.id, **payload.model_dump())
    db.add(certification)
    db.commit()
    db.refresh(certification)
    return certification


@router.post("/{vendor_id}/certifications/{certification_id}/verify")
def verify_certification(vendor_id: str, certification_id: str, user=Depends(require_roles("vendor_manager")), db: Session = Depends(get_db)):
    vendor = get_tenant_record(Vendor, vendor_id, user.organization_id, db)
    certification = db.get(VendorCertification, certification_id)
    if not certification or certification.vendor_id != vendor.id or certification.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Certification not found")
    certification.verified = True
    vendor.compliance_score = min(100, float(vendor.compliance_score) + 3)
    vendor.trust_score = vendor_score(vendor)
    db.commit()
    db.refresh(certification)
    return certification
