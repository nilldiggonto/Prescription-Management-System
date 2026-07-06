from pydantic import BaseModel, EmailStr, Field, field_validator


def _validate_password_strength(value: str) -> str:
    if not any(c.isalpha() for c in value):
        raise ValueError("Password must contain at least one letter")
    if not any(c.isdigit() for c in value):
        raise ValueError("Password must contain at least one number")
    return value


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_must_be_reasonably_strong(cls, value: str) -> str:
        return _validate_password_strength(value)


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str = Field(pattern=r"^\d{6}$", description="6-digit verification code")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(pattern=r"^\d{6}$", description="6-digit reset code")
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def new_password_must_be_reasonably_strong(cls, value: str) -> str:
        return _validate_password_strength(value)


class MessageResponse(BaseModel):
    message: str
