from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TenantRecord


class RFQ(TenantRecord, Base):
    __tablename__ = "rfqs"
    rfq_number: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    budget: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    deadline: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    invited_vendors: Mapped[int] = mapped_column(nullable=False, default=0)


class RFQItem(TenantRecord, Base):
    __tablename__ = "rfq_items"
    rfq_id: Mapped[str] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=1)
    unit: Mapped[str] = mapped_column(String(40), nullable=False, default="each")
    specifications: Mapped[str | None] = mapped_column(Text)


class Bid(TenantRecord, Base):
    __tablename__ = "bids"
    rfq_id: Mapped[str] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), index=True)
    vendor_id: Mapped[str] = mapped_column(ForeignKey("vendors.id"), index=True)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    technical_score: Mapped[int] = mapped_column(nullable=False, default=70)
    delivery_days: Mapped[int] = mapped_column(nullable=False, default=30)
    warranty_months: Mapped[int] = mapped_column(nullable=False, default=12)
    proposal: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="submitted")


class Approval(TenantRecord, Base):
    __tablename__ = "approvals"
    object_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    object_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    requested_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    comment: Mapped[str | None] = mapped_column(Text)


class Contract(TenantRecord, Base):
    __tablename__ = "contracts"
    contract_number: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    vendor_id: Mapped[str] = mapped_column(ForeignKey("vendors.id"), index=True)
    rfq_id: Mapped[str | None] = mapped_column(ForeignKey("rfqs.id"))
    bid_id: Mapped[str | None] = mapped_column(ForeignKey("bids.id"))
    contract_type: Mapped[str] = mapped_column(String(60), nullable=False, default="Services")
    value: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    blockchain_status: Mapped[str] = mapped_column(String(30), nullable=False, default="not_recorded")


class PurchaseOrder(TenantRecord, Base):
    __tablename__ = "purchase_orders"
    po_number: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    vendor_id: Mapped[str] = mapped_column(ForeignKey("vendors.id"), index=True)
    contract_id: Mapped[str | None] = mapped_column(ForeignKey("contracts.id"))
    rfq_id: Mapped[str | None] = mapped_column(ForeignKey("rfqs.id"))
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    expected_delivery: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")


class PurchaseOrderItem(TenantRecord, Base):
    __tablename__ = "purchase_order_items"
    purchase_order_id: Mapped[str] = mapped_column(ForeignKey("purchase_orders.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
