from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class RoleEnum(str, enum.Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.user, nullable=False)
    created_at = Column(DateTime, default=func.now())

    predictions = relationship(
        "Prediction", back_populates="user", cascade="all, delete-orphan"
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    brand = Column(String)
    model = Column(String)
    year = Column(Integer)
    mileage = Column(Integer)
    color = Column(String)
    body_type = Column(String)
    auto_class = Column(String)
    owners_number = Column(Integer)
    accidents = Column(String)
    engine_type = Column(String)
    transmission = Column(String)
    gear_type = Column(String)
    displacement = Column(Float)
    power = Column(Integer)
    description = Column(String, nullable=True)
    region = Column(String)

    predicted_price = Column(Float)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="predictions")
