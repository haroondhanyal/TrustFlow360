"""Create a small local-only TrustFlow walkthrough workspace."""
from datetime import date, timedelta

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Organization, User
from app.operations import OperationRecord
from app.organization.models import Department
from app.procurement.models import Approval, Bid, Contract, PurchaseOrder, PurchaseOrderItem, RFQ, RFQItem
from app.vendors.models import Vendor, VendorCertification

VENDOR_SEEDS = [
    ("Northstar Logistics", "Logistics", "Singapore", 96, 94),
    ("Meridian Supply Co.", "Industrial supplies", "Pakistan", 91, 88),
    ("Atlas Components", "Electronics", "Germany", 82, 84),
    ("Verity Assurance", "Professional services", "United Kingdom", 98, 91),
    ("NexWave Systems", "Technology", "United States", 88, 86),
]


def seed_operations(db, organization: Organization, admin: User, vendors: list[Vendor]) -> None:
    examples = [
        ("shipments", "Regional equipment shipment", "in_transit", {"carrier": "Demo Freight", "tracking_number": "TF-2026-001", "origin": "Karachi", "destination": "Lahore", "expected_delivery": (date.today() + timedelta(days=3)).isoformat()}),
        ("finance", "Quarterly freight invoice", "open", {"vendor": vendors[0].name, "invoice_number": "INV-DEMO-001", "amount": 18250, "currency": "USD", "due_date": (date.today() + timedelta(days=14)).isoformat()}),
        ("risks", "Single-route carrier dependency", "open", {"category": "Supply chain", "severity": "medium", "owner": "Procurement", "review_date": (date.today() + timedelta(days=30)).isoformat()}),
        ("credentials", "ISO 27001 · Northstar Logistics", "verified", {"issuer": "ISO", "credential_type": "Security certification", "reference": "ISO-27001-2026", "expires_on": (date.today() + timedelta(days=365)).isoformat()}),
        ("assets", "Regional network switch lot", "active", {"asset_tag": "AST-DEMO-001", "category": "Network equipment", "location": "Lahore office", "custodian": "IT Operations"}),
    ]
    for record_type, name, status, data in examples:
        exists = db.scalar(select(OperationRecord.id).where(OperationRecord.organization_id == organization.id, OperationRecord.record_type == record_type, OperationRecord.name == name))
        if not exists:
            db.add(OperationRecord(organization_id=organization.id, created_by=admin.id, record_type=record_type, name=name, status=status, data=data))


def seed() -> None:
    settings = get_settings()
    if settings.app_env != "development":
        raise RuntimeError("Demo seed data can only be created when APP_ENV=development")
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        organization = db.scalar(select(Organization).where(Organization.slug == "nexatel-demo"))
        if organization:
            admin = db.scalar(select(User).where(User.organization_id == organization.id, User.role == "organization_admin"))
            vendors = db.scalars(select(Vendor).where(Vendor.organization_id == organization.id).order_by(Vendor.created_at)).all()
            if admin and vendors:
                seed_operations(db, organization, admin, vendors)
                db.commit()
            print("NexaTel demo workspace checked and Phase 4 examples added if missing")
            return
        organization = Organization(name="NexaTel Communications", workspace_name="NexaTel", slug="nexatel-demo", industry="Telecommunications", company_size="1,001-5,000", country="Pakistan")
        db.add(organization)
        db.flush()
        admin = User(organization_id=organization.id, email="admin@demo.local", first_name="Sofia", last_name="Khan", password_hash=hash_password("Demo-TrustFlow-123!"), role="organization_admin")
        db.add(admin)
        db.flush()
        department = Department(organization_id=organization.id, created_by=admin.id, name="Procurement", description="Strategic sourcing and supplier operations")
        db.add(department)
        vendors = []
        for index, (name, category, country, trust, delivery) in enumerate(VENDOR_SEEDS, 1):
            vendor = Vendor(organization_id=organization.id, created_by=admin.id, vendor_number=f"VEN-{index:04d}", name=name, category=category, country=country, verification_status="verified", risk_level="low" if trust >= 90 else "medium", status="active", trust_score=trust, delivery_score=delivery, compliance_score=trust - 2, tax_id=f"TX-{index:04d}", registration_number=f"REG-{index:04d}", contact_name=f"Partner {index}", contact_email=f"vendor{index}@demo.local")
            db.add(vendor)
            vendors.append(vendor)
        db.flush()
        certification = VendorCertification(organization_id=organization.id, created_by=admin.id, vendor_id=vendors[0].id, name="ISO 27001", issuer="International Standards Organization", certificate_number="ISO-27001-2026", status="valid", issued_on=date.today().isoformat(), expires_on=(date.today() + timedelta(days=365)).isoformat(), verified=True)
        rfq = RFQ(organization_id=organization.id, created_by=admin.id, rfq_number=f"RFQ-{date.today().year}-0001", title="Regional network equipment refresh", department="Procurement", description="Switches and edge equipment for regional office rollout", budget=72000, currency="USD", deadline=date.today() + timedelta(days=20), status="open", invited_vendors=3)
        db.add_all([certification, rfq])
        db.flush()
        db.add(RFQItem(organization_id=organization.id, created_by=admin.id, rfq_id=rfq.id, name="Enterprise network switch", quantity=24, unit="units", specifications="Layer 3, 48 ports, 10 GbE uplinks"))
        db.flush()
        bid = Bid(organization_id=organization.id, created_by=admin.id, rfq_id=rfq.id, vendor_id=vendors[4].id, amount=68400, technical_score=92, delivery_days=21, warranty_months=36, proposal="Includes rollout support and three-year warranty.", status="submitted")
        contract = Contract(organization_id=organization.id, created_by=admin.id, contract_number=f"CTR-{date.today().year}-0001", title="Annual logistics services", vendor_id=vendors[0].id, contract_type="Services", value=148000, start_date=date.today(), end_date=date.today() + timedelta(days=365), status="active", blockchain_status="not_recorded")
        db.add_all([bid, contract])
        db.flush()
        order = PurchaseOrder(organization_id=organization.id, created_by=admin.id, po_number=f"PO-{date.today().year}-0001", title="Quarterly regional freight", vendor_id=vendors[0].id, contract_id=contract.id, amount=18250, expected_delivery=date.today() + timedelta(days=14), status="approved")
        db.add(order)
        db.flush()
        db.add(PurchaseOrderItem(purchase_order_id=order.id, organization_id=organization.id, created_by=admin.id, name="Regional freight pallet", quantity=5, unit_price=3650))
        approval = Approval(organization_id=organization.id, created_by=admin.id, requested_by=admin.id, object_type="purchase_order", object_id=order.id, title="Sample approval: software renewal", status="pending")
        db.add(approval)
        seed_operations(db, organization, admin, vendors)
        db.commit()
        print("Demo workspace created: admin@demo.local / Demo-TrustFlow-123!")


if __name__ == "__main__":
    seed()
