from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import datetime
from app.models import RoleEnum


class UserRegister(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Пароль слишком длинный (максимум 72 символа)")
        if len(v) < 6:
            raise ValueError("Пароль слишком короткий (минимум 6 символов)")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    role: RoleEnum
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class PredictRequest(BaseModel):
    brand: str
    model: str
    year: int
    mileage: int
    color: str
    body_type: str
    auto_class: str
    owners_number: int
    accidents: str
    engine_type: str
    transmission: str
    gear_type: str
    displacement: float
    power: int
    description: str = ""
    region: str


class PredictResponse(BaseModel):
    predicted_price: float
    text_keywords: list[str] = []


class PredictionResponse(BaseModel):
    id: int
    brand: str
    model: str
    year: int
    mileage: int
    color: str
    body_type: str
    auto_class: str
    owners_number: int
    accidents: str
    engine_type: str
    transmission: str
    gear_type: str
    displacement: float
    power: int
    predicted_price: float
    created_at: datetime
    region: str

    model_config = ConfigDict(from_attributes=True)


class UserAdminResponse(BaseModel):
    id: int
    email: str
    role: RoleEnum
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
