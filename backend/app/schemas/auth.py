from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_must_be_reasonably_strong(cls, value: str) -> str:
        if not any(c.isalpha() for c in value):
            raise ValueError("Password must contain at least one letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one number")
        return value


class VerifyEmailResponse(BaseModel):
    message: str
