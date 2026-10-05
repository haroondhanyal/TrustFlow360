"""Create a small local-only TrustFlow walkthrough workspace."""
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from secrets import token_urlsafe

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import fingerprint, hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Organization, User
from app.operations import OperationRecord, ProofRecord
from app.organization.models import Department, Invitation, Role
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


def ensure_demo_dataset(db, organization: Organization, admin: User) -> None:
    """Keep the development workspace populated and safe to seed repeatedly."""
    department_names = ["Procurement", "Finance", "Legal", "Technology", "Operations", "Security", "Logistics", "Compliance", "Facilities", "Human Resources", "Engineering", "Customer Success", "Field Services", "Product", "Data", "Quality", "Marketing", "Sales", "Strategy", "Risk", "Sustainability", "Research", "Supplier Relations", "Regional Delivery", "Executive"]
    departments = db.scalars(select(Department).where(Department.organization_id == organization.id).order_by(Department.name)).all()
    department_by_name = {row.name: row for row in departments}
    for name in department_names:
        if name not in department_by_name:
            row = Department(organization_id=organization.id, created_by=admin.id, name=name, description=f"{name} team workspace")
            db.add(row)
            department_by_name[name] = row
    db.flush()
    department_ids = list(department_by_name.values())

    roles = [
        ("procurement_manager", "buyer", 3), ("vendor_manager", "vendor", 3),
        ("finance_manager", "finance", 3), ("auditor", "audit", 3), ("viewer", "member", 7),
    ]
    for role, prefix, count in roles:
        for index in range(1, count + 1):
            email = f"{prefix}{index:02d}@example.com"
            person = db.scalar(select(User).where(User.email == email))
            if not person:
                person = User(organization_id=organization.id, email=email, first_name=prefix.title(), last_name=f"Member {index:02d}", password_hash=hash_password(f"TF360-{prefix.title()}{index:02d}-2026!"), role=role, department_id=department_ids[(index + len(prefix)) % len(department_ids)].id)
                db.add(person)
    db.flush()

    custom_roles = [
        ("Regional Buyer", ["vendors.view", "rfqs.manage", "bids.manage"]),
        ("Category Owner", ["vendors.view", "rfqs.manage", "contracts.view"]),
        ("Supplier Reviewer", ["vendors.view", "vendors.manage", "trust_passports.manage"]),
        ("Compliance Lead", ["organization.view", "vendors.view", "contracts.view"]),
        ("Accounts Payable", ["purchase_orders.view", "purchase_orders.approve"]),
        ("Read Only Analyst", ["organization.view", "vendors.view", "procurement.view"]),
        ("Sourcing Lead", ["rfqs.manage", "bids.manage", "contracts.manage"]),
        ("Logistics Coordinator", ["vendors.view", "procurement.view"]),
        ("Contract Reviewer", ["contracts.view", "procurement.view"]),
        ("Risk Analyst", ["organization.view", "vendors.view"]),
        ("Regional Finance", ["purchase_orders.view", "purchase_orders.approve"]),
        ("Operations Manager", ["vendors.view", "procurement.view"]),
        ("Quality Reviewer", ["vendors.view", "trust_passports.manage"]),
        ("Executive Viewer", ["organization.view", "procurement.view"]),
        ("Vendor Onboarding", ["vendors.manage", "trust_passports.manage"]),
        ("Purchase Approver", ["purchase_orders.approve"]),
        ("Sustainability Auditor", ["organization.view", "vendors.view"]),
        ("IT Asset Steward", ["organization.view"]),
        ("Security Assessor", ["vendors.view", "trust_passports.manage"]),
        ("Project Buyer", ["rfqs.manage", "bids.manage"]),
        ("Procurement Observer", ["procurement.view"]),
        ("Contract Administrator", ["contracts.manage"]),
        ("Supplier Auditor", ["vendors.view", "organization.view"]),
        ("Regional Operations", ["vendors.view", "procurement.view"]),
    ]
    for index, (name, permissions) in enumerate(custom_roles, 1):
        key = f"demo_role_{index:02d}"
        if not db.scalar(select(Role.id).where(Role.organization_id == organization.id, Role.key == key)):
            db.add(Role(organization_id=organization.id, created_by=admin.id, key=key, name=name, permissions=permissions))

    now = datetime.now(timezone.utc)
    for index in range(1, 26):
        email = f"invite{index:02d}@example.com"
        if not db.scalar(select(Invitation.id).where(Invitation.organization_id == organization.id, Invitation.email == email)):
            db.add(Invitation(organization_id=organization.id, created_by=admin.id, email=email, role=["viewer", "auditor", "vendor_manager"][index % 3], department_id=department_ids[index % len(department_ids)].id, token_hash=fingerprint(f"trustflow-demo-invite-{index:02d}"), expires_at=now + timedelta(days=7), accepted_at=(now - timedelta(days=1) if index % 4 == 0 else None)))

    vendors = db.scalars(select(Vendor).where(Vendor.organization_id == organization.id).order_by(Vendor.vendor_number)).all()
    vendor_names = ["Apex Industrial", "Harborline Freight", "Cedar Peak Consulting", "Orion Network Systems", "Blue Coast Components", "Pioneer Safety Group", "Summit Cloud Services", "Golden Gate Packaging", "Evergreen Energy Partners", "Quantum Field Services", "Silverline Manufacturing", "Cobalt Security Labs", "Redwood Medical Supply", "Vertex Data Solutions", "Crescent Facilities", "Pacific Rail Logistics", "Northwind Analytics", "Clearwater Compliance", "Ironwood Equipment", "Brightpath Training", "Urban Link Telecom", "TerraNova Materials", "Keystone Engineering", "Cloudline Software", "Atlas Field Logistics"]
    countries = ["Pakistan", "Singapore", "Germany", "United Kingdom", "United States", "United Arab Emirates", "Japan", "Australia", "Canada", "Netherlands"]
    categories = ["Logistics", "Technology", "Manufacturing", "Professional services", "Industrial supplies", "Security", "Energy", "Facilities"]
    for index in range(len(vendors) + 1, 31):
        offset = index - 6
        name = vendor_names[offset]
        vendor = Vendor(organization_id=organization.id, created_by=admin.id, vendor_number=f"VEN-{index:04d}", name=name, category=categories[index % len(categories)], country=countries[index % len(countries)], website=f"https://vendor{index:02d}.example.com", registration_number=f"REG-{index:04d}", tax_id=f"TX-{index:04d}", contact_name=f"Partner {index:02d}", contact_email=f"vendor{index:02d}@example.com", verification_status="pending" if index % 9 == 0 else "verified", risk_level=["low", "medium", "high"][index % 3], status="active", trust_score=60 + (index * 7) % 40, delivery_score=58 + (index * 9) % 42, compliance_score=55 + (index * 11) % 45, active_contracts=index % 5, notes="Seeded development supplier profile")
        db.add(vendor)
    db.flush()
    vendors = db.scalars(select(Vendor).where(Vendor.organization_id == organization.id).order_by(Vendor.vendor_number)).all()
    for index, vendor in enumerate(vendors, 1):
        if not db.scalar(select(VendorCertification.id).where(VendorCertification.organization_id == organization.id, VendorCertification.vendor_id == vendor.id)):
            db.add(VendorCertification(organization_id=organization.id, created_by=admin.id, vendor_id=vendor.id, name=["ISO 27001", "ISO 9001", "SOC 2 Type II", "Environmental Management"][index % 4], issuer="TrustFlow Demo Registrar", certificate_number=f"CERT-{index:04d}", status="valid" if index % 5 else "expiring", issued_on=(date.today() - timedelta(days=180)).isoformat(), expires_on=(date.today() + timedelta(days=365 if index % 5 else 30)).isoformat(), verified=index % 4 != 0))
    db.flush()

    rfqs = db.scalars(select(RFQ).where(RFQ.organization_id == organization.id).order_by(RFQ.rfq_number)).all()
    departments_text = list(department_names)
    for index in range(len(rfqs) + 1, 31):
        status = ["open", "draft", "pending_approval", "evaluation", "awarded", "open"][index % 6]
        rfq = RFQ(organization_id=organization.id, created_by=admin.id, rfq_number=f"RFQ-{date.today().year}-{index:04d}", title=f"{['Network refresh','Regional freight','Security assessment','Office equipment','Cloud migration'][index % 5]} · {index:02d}", department=departments_text[index % len(departments_text)], description=f"Development sample sourcing event {index:02d} with evaluation criteria and delivery requirements.", budget=15000 + index * 475, currency="USD", deadline=date.today() + timedelta(days=10 + index), status=status, invited_vendors=3 + index % 12)
        db.add(rfq)
        db.flush()
        for item_index in range(1, 2 + index % 3):
            db.add(RFQItem(organization_id=organization.id, created_by=admin.id, rfq_id=rfq.id, name=f"Required line item {item_index} · RFQ {index:02d}", quantity=item_index * 5, unit="units", specifications=f"Commercial-grade specification {index:02d}-{item_index:02d}"))
    db.flush()
    rfqs = db.scalars(select(RFQ).where(RFQ.organization_id == organization.id).order_by(RFQ.rfq_number)).all()

    eligible_vendors = [vendor for vendor in vendors if vendor.verification_status == "verified" and vendor.status == "active"]
    bids = db.scalars(select(Bid).where(Bid.organization_id == organization.id).order_by(Bid.created_at)).all()
    for index in range(len(bids) + 1, 31):
        rfq = rfqs[(index - 1) % len(rfqs)]
        vendor = eligible_vendors[(index - 1) % len(eligible_vendors)]
        bid_status = ["submitted", "submitted", "declined", "submitted", "awarded"][index % 5]
        db.add(Bid(organization_id=organization.id, created_by=admin.id, rfq_id=rfq.id, vendor_id=vendor.id, amount=12000 + index * 617, technical_score=55 + index % 46, delivery_days=7 + index % 90, warranty_months=12 + index % 48, proposal=f"Sample proposal {index:02d}: delivery, warranty and support plan.", status=bid_status))
        if bid_status == "awarded":
            rfq.status = "awarded"
    db.flush()

    contracts = db.scalars(select(Contract).where(Contract.organization_id == organization.id).order_by(Contract.contract_number)).all()
    for index in range(len(contracts) + 1, 31):
        vendor = eligible_vendors[(index - 1) % len(eligible_vendors)]
        db.add(Contract(organization_id=organization.id, created_by=admin.id, contract_number=f"CTR-{date.today().year}-{index:04d}", title=f"{vendor.name} · Agreement {index:02d}", vendor_id=vendor.id, rfq_id=rfqs[(index - 1) % len(rfqs)].id, contract_type=["Services", "Goods", "Framework", "SaaS"][index % 4], value=25000 + index * 3850, start_date=date.today() - timedelta(days=index * 3), end_date=date.today() + timedelta(days=365 - index * 2), status=["active", "pending_approval", "draft", "active", "expired"][index % 5], blockchain_status="not_recorded"))
    db.flush()
    contracts = db.scalars(select(Contract).where(Contract.organization_id == organization.id).order_by(Contract.contract_number)).all()

    orders = db.scalars(select(PurchaseOrder).where(PurchaseOrder.organization_id == organization.id).order_by(PurchaseOrder.po_number)).all()
    for index in range(len(orders) + 1, 31):
        vendor = eligible_vendors[(index - 1) % len(eligible_vendors)]
        order = PurchaseOrder(organization_id=organization.id, created_by=admin.id, po_number=f"PO-{date.today().year}-{index:04d}", title=f"Regional delivery batch {index:02d}", vendor_id=vendor.id, contract_id=contracts[(index - 1) % len(contracts)].id, rfq_id=rfqs[(index - 1) % len(rfqs)].id, amount=5000 + index * 1275, expected_delivery=date.today() + timedelta(days=3 + index), status=["approved", "pending_approval", "draft", "approved", "rejected"][index % 5])
        db.add(order)
        db.flush()
        db.add(PurchaseOrderItem(organization_id=organization.id, created_by=admin.id, purchase_order_id=order.id, name=f"Fulfillment line {index:02d}", quantity=2 + index % 8, unit_price=(5000 + index * 1275) / (2 + index % 8)))
    db.flush()
    orders = db.scalars(select(PurchaseOrder).where(PurchaseOrder.organization_id == organization.id).order_by(PurchaseOrder.po_number)).all()

    approvals = db.scalars(select(Approval).where(Approval.organization_id == organization.id)).all()
    approval_sources = [("rfq", row.id, f"Publish review · {row.rfq_number}") for row in rfqs] + [("contract", row.id, f"Contract review · {row.contract_number}") for row in contracts] + [("purchase_order", row.id, f"Order review · {row.po_number}") for row in orders]
    for index in range(len(approvals) + 1, 31):
        object_type, object_id, title = approval_sources[index % len(approval_sources)]
        db.add(Approval(organization_id=organization.id, created_by=admin.id, requested_by=admin.id, object_type=object_type, object_id=object_id, title=f"{title} · {index:02d}", status=["pending", "approved", "rejected"][index % 3], comment=None if index % 3 == 0 else "Reviewed against the development approval policy"))
    db.flush()

    op_specs = {
        "shipments": ("Shipment", ["open", "in_transit", "delivered", "delayed"], ["carrier", "tracking_number", "origin", "destination", "expected_delivery"]),
        "finance": ("Invoice", ["open", "paid", "overdue", "approved"], ["vendor", "invoice_number", "amount", "currency", "due_date"]),
        "risks": ("Risk", ["open", "mitigated", "accepted"], ["category", "severity", "owner", "review_date"]),
        "credentials": ("Credential", ["open", "verified", "revoked"], ["issuer", "credential_type", "reference", "expires_on"]),
        "assets": ("Asset", ["open", "active", "retired"], ["asset_tag", "category", "location", "custodian"]),
    }
    for kind, (label, statuses, _) in op_specs.items():
        existing = db.scalars(select(OperationRecord).where(OperationRecord.organization_id == organization.id, OperationRecord.record_type == kind).order_by(OperationRecord.created_at)).all()
        for index in range(len(existing) + 1, 31):
            vendor = vendors[(index - 1) % len(vendors)]
            data = {
                "shipments": {"carrier": f"Carrier {index % 8 + 1}", "tracking_number": f"TF-SHP-{index:04d}", "origin": countries[index % len(countries)], "destination": countries[(index + 3) % len(countries)], "expected_delivery": (date.today() + timedelta(days=index - 15)).isoformat()},
                "finance": {"vendor": vendor.name, "invoice_number": f"INV-{date.today().year}-{index:04d}", "amount": 2500 + index * 975, "currency": "USD", "due_date": (date.today() + timedelta(days=index - 15)).isoformat()},
                "risks": {"category": categories[index % len(categories)], "severity": ["low", "medium", "high", "critical"][index % 4], "owner": department_names[index % len(department_names)], "review_date": (date.today() + timedelta(days=index)).isoformat()},
                "credentials": {"issuer": "TrustFlow Demo Registrar", "credential_type": ["Security", "Quality", "Environmental", "Insurance"][index % 4], "reference": f"CRED-{index:04d}", "expires_on": (date.today() + timedelta(days=index * 12 - 80)).isoformat()},
                "assets": {"asset_tag": f"AST-{index:04d}", "category": categories[index % len(categories)], "location": countries[index % len(countries)], "custodian": department_names[index % len(department_names)]},
            }[kind]
            db.add(OperationRecord(organization_id=organization.id, created_by=admin.id, record_type=kind, name=f"{label} record {index:02d}", status=statuses[index % len(statuses)], data=data))
    db.flush()

    proofs = db.scalars(select(ProofRecord).where(ProofRecord.organization_id == organization.id).order_by(ProofRecord.created_at)).all()
    proof_records = db.scalars(select(OperationRecord).where(OperationRecord.organization_id == organization.id).order_by(OperationRecord.created_at)).all()
    previous_digest = proofs[-1].digest if proofs else None
    for index in range(len(proofs) + 1, 31):
        record = proof_records[(index - 1) % len(proof_records)]
        statement = {"type": record.record_type, "id": record.id, "name": record.name, "status": record.status, "data": record.data or {}, "created_at": record.created_at.isoformat()}
        raw = json.dumps({"statement": statement, "previous": previous_digest}, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(raw.encode()).hexdigest()
        db.add(ProofRecord(organization_id=organization.id, created_by=admin.id, subject_type=record.record_type, subject_id=record.id, digest=digest, previous_digest=previous_digest, statement=statement))
        previous_digest = digest
        db.flush()


def seed() -> None:
    settings = get_settings()
    if settings.app_env != "development":
        raise RuntimeError("Demo seed data can only be created when APP_ENV=development")
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        organization = db.scalar(select(Organization).where(Organization.slug == "nexatel-demo"))
        if organization:
            admin = db.scalar(select(User).where(User.organization_id == organization.id, User.role == "organization_admin"))
            if admin and admin.email == "admin@demo.local":
                admin.email = "admin@example.com"
            vendors = db.scalars(select(Vendor).where(Vendor.organization_id == organization.id).order_by(Vendor.created_at)).all()
            if admin:
                ensure_demo_dataset(db, organization, admin)
                db.commit()
            print("NexaTel demo workspace checked and all sample records added if missing")
            return
        organization = Organization(name="NexaTel Communications", workspace_name="NexaTel", slug="nexatel-demo", industry="Telecommunications", company_size="1,001-5,000", country="Pakistan")
        db.add(organization)
        db.flush()
        admin = User(organization_id=organization.id, email="admin@example.com", first_name="Sofia", last_name="Khan", password_hash=hash_password("Demo-TrustFlow-123!"), role="organization_admin")
        db.add(admin)
        db.flush()
        department = Department(organization_id=organization.id, created_by=admin.id, name="Procurement", description="Strategic sourcing and supplier operations")
        db.add(department)
        vendors = []
        for index, (name, category, country, trust, delivery) in enumerate(VENDOR_SEEDS, 1):
            vendor = Vendor(organization_id=organization.id, created_by=admin.id, vendor_number=f"VEN-{index:04d}", name=name, category=category, country=country, verification_status="verified", risk_level="low" if trust >= 90 else "medium", status="active", trust_score=trust, delivery_score=delivery, compliance_score=trust - 2, tax_id=f"TX-{index:04d}", registration_number=f"REG-{index:04d}", contact_name=f"Partner {index}", contact_email=f"vendor{index}@example.com")
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
        ensure_demo_dataset(db, organization, admin)
        db.commit()
        print("Demo workspace created: admin@example.com / Demo-TrustFlow-123!")


if __name__ == "__main__":
    seed()
