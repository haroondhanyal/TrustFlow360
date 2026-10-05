import base64
import binascii

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
    role: str
    avatar_data: str | None = None


class UserProfileUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    avatar_data: str | None = Field(default=None, max_length=1_000_000)

    @field_validator("avatar_data")
    @classmethod
    def validate_avatar(cls, value: str | None):
        if value is None:
            return value
        try:
            header, encoded = value.split(",", 1)
            if header not in {"data:image/jpeg;base64", "data:image/png;base64", "data:image/webp;base64"}:
                raise ValueError("Use a JPEG, PNG or WebP profile photo.")
            decoded = base64.b64decode(encoded, validate=True)
            if not decoded or len(decoded) > 750_000:
                raise ValueError("Profile photos must be smaller than 750 KB.")
        except (ValueError, binascii.Error):
            raise ValueError("Upload a valid JPEG, PNG or WebP image under 750 KB.") from None
        return value


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
