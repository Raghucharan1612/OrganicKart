from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.roles import RoleEnum

PUBLIC_SIGNUP_ROLES = {
    RoleEnum.CUSTOMER,
    RoleEnum.FARMER,
    RoleEnum.VENDOR,
    RoleEnum.DELIVERY_PARTNER,
}


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    phone: str | None = Field(default=None, max_length=20)
    role: RoleEnum = RoleEnum.CUSTOMER

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: RoleEnum) -> RoleEnum:
        if value not in PUBLIC_SIGNUP_ROLES:
            raise ValueError(
                "Self-registration is only allowed for CUSTOMER, FARMER, "
                "VENDOR, or DELIVERY_PARTNER roles."
            )
        return value

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit.")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one letter.")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    phone: str | None
    role: RoleEnum
    is_active: bool
    is_verified: bool


class UserProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    phone: str | None
    role: RoleEnum
    is_active: bool
    is_verified: bool


class UserProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=20)


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit.")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one letter.")
        return value
