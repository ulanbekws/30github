from typing import Optional
from pydantic import BaseModel, UUID4

from src.products.models import Product


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float


class ProductResponse(ProductCreate):
    id: int
    created_at: str

    class Config:
        from_attributes = True


class ToDoSchema(BaseModel):
    id: Optional[UUID4] = None
    title: str
    description: str
    completed: Optional[bool] = False




