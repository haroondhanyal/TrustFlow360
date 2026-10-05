from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def new_id() -> str:
    return str(uuid4())


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    workspace_name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    website: Mapped[str | None] = mapped_column(String(255))
    industry: Mapped[str | None] = mapped_column(String(100))
    company_size: Mapped[str | None] = mapped_column(String(50))
    country: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)
    users: Mapped[list["User"]] = relationship(back_populates="organization")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("organization_id", "email", name="uq_user_org_email"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="organization_admin")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)
    organization: Mapped[Organization | None] = relationship(back_populates="users")


class RefreshSession(Base):
    __tablename__ = "refresh_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
