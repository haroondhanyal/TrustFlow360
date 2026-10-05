"""Phase 4 operational records and local hash-chain proofs."""
from alembic import op
import sqlalchemy as sa

revision = "0003_operations"
down_revision = "0002_trust_procurement"
branch_labels = None
depends_on = None


def tenant_columns():
    return [sa.Column("id", sa.String(36), primary_key=True), sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False), sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False)]


def upgrade():
    op.create_table("operation_records", *tenant_columns(), sa.Column("record_type", sa.String(40), nullable=False), sa.Column("name", sa.String(200), nullable=False), sa.Column("status", sa.String(40), nullable=False), sa.Column("data", sa.JSON(), nullable=False))
    op.create_index("ix_operation_records_organization_id", "operation_records", ["organization_id"])
    op.create_index("ix_operation_records_record_type", "operation_records", ["record_type"])
    op.create_table("proof_records", *tenant_columns(), sa.Column("subject_type", sa.String(40), nullable=False), sa.Column("subject_id", sa.String(36), nullable=False), sa.Column("digest", sa.String(64), nullable=False, unique=True), sa.Column("previous_digest", sa.String(64)), sa.Column("statement", sa.JSON(), nullable=False))
    op.create_index("ix_proof_records_organization_id", "proof_records", ["organization_id"])
    op.create_index("ix_proof_records_subject_id", "proof_records", ["subject_id"])


def downgrade():
    op.drop_index("ix_proof_records_subject_id", table_name="proof_records")
    op.drop_index("ix_proof_records_organization_id", table_name="proof_records")
    op.drop_table("proof_records")
    op.drop_index("ix_operation_records_record_type", table_name="operation_records")
    op.drop_index("ix_operation_records_organization_id", table_name="operation_records")
    op.drop_table("operation_records")
