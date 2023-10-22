from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Todos
from db import SessionLocal
from todo_post_model import TodoRequest

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/")
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@router.get("/todo/{id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, id: int = Path(gt=0)):
    model = db.query(Todos).filter(Todos.id == id).first()
    if model is not None:
        return model

    raise HTTPException(status_code=404, detail='Content is not found.')


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, req: TodoRequest):
    todo_model = Todos(**req.model_dump())
    db.add(todo_model)
    db.commit()


@router.put("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def updated_todo(db: db_dependency, req: TodoRequest, id: int = Path(gt=0)):
    model = db.query(Todos).filter(Todos.id == id).first()
    if model is None:
        raise HTTPException(status_code=404, detail='Content is not found.')

    model.title = req.title
    model.description = req.description
    model.priority = req.priority
    model.complete = req.complete

    db.add(model)
    db.commit()


@router.delete("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, id: int = Path(gt=0)):
    model = db.query(Todos).filter(Todos.id == id).first()
    if model is None:
        raise HTTPException(status_code=404, detail='Content is not found.')

    db.query(Todos).filter(Todos.id == id).delete()
    db.commit()