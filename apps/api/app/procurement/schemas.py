from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class RFQItemInput(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    quantity: float = Field(gt=0)
    unit: str = Field(default="each", max_length=40)
    specifications: str | None = Field(default=None, max_length=2000)


class RFQCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    department: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=5000)
    budget: float = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    deadline: date
    invited_vendors: int = Field(default=0, ge=0)
    items: list[RFQItemInput] = Field(default_factory=list, max_length=100)


class BidCreate(BaseModel):
    vendor_id: str
    amount: float = Field(gt=0)
    technical_score: int = Field(default=70, ge=0, le=100)
    delivery_days: int = Field(default=30, ge=1, le=3650)
    warranty_months: int = Field(default=12, ge=0, le=600)
    proposal: str | None = Field(default=None, max_length=5000)


class ContractCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    vendor_id: str
    rfq_id: str | None = None
    bid_id: str | None = None
    contract_type: str = Field(default="Services", max_length=60)
    value: float = Field(gt=0)
    start_date: date
    end_date: date


class PurchaseOrderItemInput(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    quantity: float = Field(gt=0)
    unit_price: float = Field(gt=0)


class PurchaseOrderCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    vendor_id: str
    contract_id: str | None = None
    rfq_id: str | None = None
    amount: float = Field(gt=0)
    expected_delivery: date | None = None
    items: list[PurchaseOrderItemInput] = Field(default_factory=list, max_length=100)


class DecisionInput(BaseModel):
    decision: str = Field(pattern=r"^(approve|reject|award|decline)$")
    comment: str | None = Field(default=None, max_length=2000)


class EntityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
