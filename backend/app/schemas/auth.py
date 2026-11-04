from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email superadmin")
    password: str = Field(..., description="Password superadmin")


class LoginResponse(BaseModel):
    status: str = "success"
    access_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    status: str = "success"
    message: str = "Logout berhasil."
