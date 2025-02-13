from pydantic import BaseModel

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
    id: int | None
    title: str
    description: str | None = None
    completed: bool = False




