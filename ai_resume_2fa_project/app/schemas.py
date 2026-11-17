from pydantic import BaseModel, EmailStr, Field

class ParsedResume(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    skills: list[str] = []
    experience: str | None = None

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: str | None = None
    password: str = Field(min_length=8)
    skills: list[str] = []
    experience: str | None = None
    qualification: str | None = None
    totp_secret: str | None = None

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)
    channel: str = "email"

class ProfileUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    skills: list[str] | None = None
    experience: str | None = None
    qualification: str | None = None
