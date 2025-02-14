from fastapi import APIRouter
from fastapi.responses import JSONResponse
import uuid

from pydantic import UUID4

from src.config import connect_db
from src.products.schemas import ToDoSchema

router = APIRouter()


@router.get("/")
async def get_products():
    return None


@router.post("/todos/", status_code=201)
async def create_todo(todo_data: ToDoSchema):
    todo_data.id = uuid.uuid4()
    conn = await connect_db()
    await conn.execute("INSERT INTO todo.todo (id, title, description, completed) VALUES ($1, $2, $3, $4)",
                       todo_data.id,
                       todo_data.title,
                       todo_data.description,
                       todo_data.completed)
    await close_db(conn)
    return todo_data


@router.get("/todos/")
async def read_todos(todo_id: UUID4):
    conn = await connect_db()
    row = await conn.fetchrow("SELECT * FROM todo.todo WHERE id=$1", todo_id)
    await close_db(conn)
    return row


@router.post("/todos/update/")
async def update_todo(todo: ToDoSchema):
    conn = await connect_db()
    row = await conn.fetchrow("UPDATE todo.todo SET title=$2, description=$3, completed=$4 WHERE id=$1",
                              todo.id,
                              todo.title,
                              todo.description,
                              todo.completed)
    await close_db(conn)
    return {"message": f"Запись {todo.id} обновлена"}


@router.delete("/todo/delete/")
async def delete_todo(id_: UUID4):
    conn = await connect_db()
    row = await conn.execute("DELETE FROM todo.todo WHERE id=$1", id)
    await close_db(conn)
    return {"message": f"Запись {id} удалена."}

async def close_db(conn):
    await conn.close()