from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    slug: str = Field(min_length=2, max_length=80, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    website: str | None = Field(default=None, max_length=255)
    industry: str | None = Field(default=None, max_length=100)
    size: str | None = Field(default=None, max_length=50)
    country: str | None = Field(default=None, max_length=100)
    workspace_name: str = Field(min_length=2, max_length=200)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    organization_id: str | None


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    workspace_name: str
    slug: str
    website: str | None
    industry: str | None
    company_size: str | None
    country: str | None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
    organization: OrganizationResponse | None = None


class OrganizationSessionResponse(BaseModel):
    organization: OrganizationResponse
    access_token: str
