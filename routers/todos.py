from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Todos
from db import SessionLocal
from todo_post_model import TodoRequest
from .auth import get_user

router = APIRouter(
    tags=['Todo']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_user)]


@router.get("/")
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@router.get("/todo/{id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    model = db.query(Todos).filter(Todos.id == id).filter(Todos.owner_id == user.get('id')).first()
    if model is not None:
        return model

    raise HTTPException(status_code=404, detail='Content is not found.')


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, req: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    todo_model = Todos(**req.model_dump(), owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()


@router.put("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def updated_todo(user: user_dependency, db: db_dependency, req: TodoRequest, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    model = db.query(Todos).filter(Todos.id == id).filter(Todos.owner_id == user.get('id')).first()
    if model is None:
        raise HTTPException(status_code=404, detail='Content is not found.')

    model.title = req.title
    model.description = req.description
    model.priority = req.priority
    model.complete = req.complete

    db.add(model)
    db.commit()


@router.delete("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    model = db.query(Todos).filter(Todos.id == id).filter(Todos.owner_id == user.get('id')).first()
    if model is None:
        raise HTTPException(status_code=404, detail='Content is not found.')

    db.query(Todos).filter(Todos.id == id).filter(Todos.owner_id == user.get('id')).delete()
    db.commit()