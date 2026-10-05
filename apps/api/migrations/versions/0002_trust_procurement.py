"""Add organization, vendor trust, and procurement workflow tables."""
from alembic import op
import sqlalchemy as sa

revision = "0002_trust_procurement"
down_revision = "0001_foundation"
branch_labels = None
depends_on = None


def tenant_columns():
    return [
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def tenant_index(table: str):
    op.create_index(f"ix_{table}_organization_id", table, ["organization_id"])


def upgrade() -> None:
    op.create_table(
        "departments", *tenant_columns(),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.String(500)),
        sa.UniqueConstraint("organization_id", "name", name="uq_department_org_name"),
    )
    tenant_index("departments")
    op.create_table(
        "roles", *tenant_columns(),
        sa.Column("key", sa.String(80), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("permissions", sa.JSON(), nullable=False),
        sa.UniqueConstraint("organization_id", "key", name="uq_role_org_key"),
    )
    tenant_index("roles")
    op.create_table(
        "invitations", *tenant_columns(),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("department_id", sa.String(36), sa.ForeignKey("departments.id", ondelete="SET NULL")),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True)),
    )
    tenant_index("invitations")
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("department_id", sa.String(36)))
        batch.create_foreign_key("fk_users_department_id_departments", "departments", ["department_id"], ["id"], ondelete="SET NULL")
        batch.create_index("ix_users_department_id", ["department_id"])

    op.create_table(
        "vendors", *tenant_columns(),
        sa.Column("vendor_number", sa.String(30), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("country", sa.String(100), nullable=False),
        sa.Column("website", sa.String(255)),
        sa.Column("registration_number", sa.String(100)),
        sa.Column("tax_id", sa.String(100)),
        sa.Column("contact_name", sa.String(160)),
        sa.Column("contact_email", sa.String(320)),
        sa.Column("verification_status", sa.String(30), nullable=False),
        sa.Column("risk_level", sa.String(30), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("trust_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("delivery_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("compliance_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("active_contracts", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text()),
    )
    tenant_index("vendors")
    op.create_index("ix_vendors_vendor_number", "vendors", ["vendor_number"])
    op.create_index("ix_vendors_name", "vendors", ["name"])

    op.create_table(
        "vendor_certifications", *tenant_columns(),
        sa.Column("vendor_id", sa.String(36), sa.ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("issuer", sa.String(160)),
        sa.Column("certificate_number", sa.String(100)),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("issued_on", sa.String(10)),
        sa.Column("expires_on", sa.String(10)),
        sa.Column("verified", sa.Boolean(), nullable=False),
    )
    tenant_index("vendor_certifications")
    op.create_index("ix_vendor_certifications_vendor_id", "vendor_certifications", ["vendor_id"])

    op.create_table(
        "rfqs", *tenant_columns(),
        sa.Column("rfq_number", sa.String(30), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("department", sa.String(120), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("budget", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("deadline", sa.Date(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("invited_vendors", sa.Integer(), nullable=False),
    )
    tenant_index("rfqs")
    op.create_index("ix_rfqs_rfq_number", "rfqs", ["rfq_number"])
    op.create_table(
        "rfq_items", *tenant_columns(),
        sa.Column("rfq_id", sa.String(36), sa.ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 2), nullable=False),
        sa.Column("unit", sa.String(40), nullable=False),
        sa.Column("specifications", sa.Text()),
    )
    tenant_index("rfq_items")
    op.create_index("ix_rfq_items_rfq_id", "rfq_items", ["rfq_id"])
    op.create_table(
        "bids", *tenant_columns(),
        sa.Column("rfq_id", sa.String(36), sa.ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("vendor_id", sa.String(36), sa.ForeignKey("vendors.id"), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("technical_score", sa.Integer(), nullable=False),
        sa.Column("delivery_days", sa.Integer(), nullable=False),
        sa.Column("warranty_months", sa.Integer(), nullable=False),
        sa.Column("proposal", sa.Text()),
        sa.Column("status", sa.String(30), nullable=False),
    )
    tenant_index("bids")
    op.create_index("ix_bids_rfq_id", "bids", ["rfq_id"])
    op.create_index("ix_bids_vendor_id", "bids", ["vendor_id"])

    op.create_table(
        "approvals", *tenant_columns(),
        sa.Column("object_type", sa.String(40), nullable=False),
        sa.Column("object_id", sa.String(36), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("requested_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("comment", sa.Text()),
    )
    tenant_index("approvals")
    op.create_index("ix_approvals_object_type", "approvals", ["object_type"])
    op.create_index("ix_approvals_object_id", "approvals", ["object_id"])

    op.create_table(
        "contracts", *tenant_columns(),
        sa.Column("contract_number", sa.String(30), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("vendor_id", sa.String(36), sa.ForeignKey("vendors.id"), nullable=False),
        sa.Column("rfq_id", sa.String(36), sa.ForeignKey("rfqs.id")),
        sa.Column("bid_id", sa.String(36), sa.ForeignKey("bids.id")),
        sa.Column("contract_type", sa.String(60), nullable=False),
        sa.Column("value", sa.Numeric(14, 2), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("blockchain_status", sa.String(30), nullable=False),
    )
    tenant_index("contracts")
    op.create_index("ix_contracts_contract_number", "contracts", ["contract_number"])
    op.create_index("ix_contracts_vendor_id", "contracts", ["vendor_id"])

    op.create_table(
        "purchase_orders", *tenant_columns(),
        sa.Column("po_number", sa.String(30), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("vendor_id", sa.String(36), sa.ForeignKey("vendors.id"), nullable=False),
        sa.Column("contract_id", sa.String(36), sa.ForeignKey("contracts.id")),
        sa.Column("rfq_id", sa.String(36), sa.ForeignKey("rfqs.id")),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("expected_delivery", sa.Date()),
        sa.Column("status", sa.String(30), nullable=False),
    )
    tenant_index("purchase_orders")
    op.create_index("ix_purchase_orders_po_number", "purchase_orders", ["po_number"])
    op.create_index("ix_purchase_orders_vendor_id", "purchase_orders", ["vendor_id"])
    op.create_table(
        "purchase_order_items", *tenant_columns(),
        sa.Column("purchase_order_id", sa.String(36), sa.ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 2), nullable=False),
        sa.Column("unit_price", sa.Numeric(14, 2), nullable=False),
    )
    tenant_index("purchase_order_items")
    op.create_index("ix_purchase_order_items_purchase_order_id", "purchase_order_items", ["purchase_order_id"])


def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_constraint("fk_users_department_id_departments", type_="foreignkey")
        batch.drop_index("ix_users_department_id")
        batch.drop_column("department_id")
    for table in ("purchase_order_items", "purchase_orders", "contracts", "approvals", "bids", "rfq_items", "rfqs", "vendor_certifications", "vendors", "invitations", "roles", "departments"):
        op.drop_table(table)
