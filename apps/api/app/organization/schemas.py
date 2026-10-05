from pydantic import BaseModel, ConfigDict, EmailStr, Field


class DepartmentInput(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class DepartmentOut(DepartmentInput):
    model_config = ConfigDict(from_attributes=True)
    id: str


class UserRoleUpdate(BaseModel):
    role: str = Field(min_length=2, max_length=80)
    department_id: str | None = None


class UserOut(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    department_id: str | None
    is_active: bool


class RoleInput(BaseModel):
    key: str = Field(min_length=2, max_length=80, pattern=r"^[a-z][a-z0-9_]*$")
    name: str = Field(min_length=2, max_length=120)
    permissions: list[str] = Field(default_factory=list, max_length=80)


class InvitationInput(BaseModel):
    email: EmailStr
    role: str = Field(pattern=r"^(organization_admin|procurement_manager|vendor_manager|finance_manager|auditor|viewer)$")
    department_id: str | None = None


class InvitationAccept(BaseModel):
    token: str = Field(min_length=20, max_length=200)
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=10, max_length=128)
