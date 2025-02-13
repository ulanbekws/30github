from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, func, Float, BigInteger
from sqlalchemy.orm import sessionmaker, declarative_base, Mapped, mapped_column

from src.database import Base


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class ToDo(Base):
    __tablename__ = "todo"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    description: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)
    created_at = Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
