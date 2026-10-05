from pydantic import BaseModel, ConfigDict, EmailStr, Field


class VendorCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    category: str = Field(min_length=2, max_length=100)
    country: str = Field(min_length=2, max_length=100)
    website: str | None = Field(default=None, max_length=255)
    registration_number: str | None = Field(default=None, max_length=100)
    tax_id: str | None = Field(default=None, max_length=100)
    contact_name: str | None = Field(default=None, max_length=160)
    contact_email: EmailStr | None = None
    notes: str | None = Field(default=None, max_length=3000)


class VendorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    website: str | None = Field(default=None, max_length=255)
    registration_number: str | None = Field(default=None, max_length=100)
    tax_id: str | None = Field(default=None, max_length=100)
    contact_name: str | None = Field(default=None, max_length=160)
    contact_email: EmailStr | None = None
    notes: str | None = Field(default=None, max_length=3000)


class CertificationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    issuer: str | None = Field(default=None, max_length=160)
    certificate_number: str | None = Field(default=None, max_length=100)
    issued_on: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    expires_on: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")


class VendorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    vendor_number: str
    name: str
    category: str
    country: str
    website: str | None
    registration_number: str | None
    tax_id: str | None
    contact_name: str | None
    contact_email: str | None
    verification_status: str
    risk_level: str
    status: str
    trust_score: float
    delivery_score: float
    compliance_score: float
    active_contracts: int
    notes: str | None
