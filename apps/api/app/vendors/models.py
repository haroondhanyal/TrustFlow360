from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TenantRecord


class Vendor(TenantRecord, Base):
    __tablename__ = "vendors"
    vendor_number: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    website: Mapped[str | None] = mapped_column(String(255))
    registration_number: Mapped[str | None] = mapped_column(String(100))
    tax_id: Mapped[str | None] = mapped_column(String(100))
    contact_name: Mapped[str | None] = mapped_column(String(160))
    contact_email: Mapped[str | None] = mapped_column(String(320))
    verification_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    risk_level: Mapped[str] = mapped_column(String(30), nullable=False, default="medium")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    trust_score: Mapped[int] = mapped_column(Numeric(5, 2), nullable=False, default=60)
    delivery_score: Mapped[int] = mapped_column(Numeric(5, 2), nullable=False, default=80)
    compliance_score: Mapped[int] = mapped_column(Numeric(5, 2), nullable=False, default=60)
    active_contracts: Mapped[int] = mapped_column(nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text)


class VendorCertification(TenantRecord, Base):
    __tablename__ = "vendor_certifications"
    vendor_id: Mapped[str] = mapped_column(ForeignKey("vendors.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    issuer: Mapped[str | None] = mapped_column(String(160))
    certificate_number: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="valid")
    issued_on: Mapped[str | None] = mapped_column(String(10))
    expires_on: Mapped[str | None] = mapped_column(String(10))
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
