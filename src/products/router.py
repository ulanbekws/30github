from fastapi import APIRouter

from src.products.schemas import ToDoSchema

router = APIRouter()


@router.get("/")
async def get_products():
    return None


@router.post("/todo/")
async def create_todo(todo_data: ToDoSchema):
    pass


@router.get("/todo/{todo_id}/")
async def get_todo(todo_id: int):
    pass


@router.put("/todo/{todo_id}/")
async def put_todo(todo_id: int):
    pass


@router.delete("/todo/{todo_id}/")
async def delete_todo(todo_id: int):
    pass