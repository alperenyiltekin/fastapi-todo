from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Todos, Users
from db import SessionLocal
from user_post_model import UserVerify
from .auth import get_user
from passlib.context import CryptContext

router = APIRouter(
    prefix='/user',
    tags=['User']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_user)]
bcrypt_ctx = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verify: UserVerify):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_ctx.verify(user_verify.password, model.hashed_pwd):
        raise HTTPException(status_code=401, detail='Error on password changing')

    model.hashed_pwd = bcrypt_ctx.hash(user_verify.new_password)
    db.add(model)
    db.commit()
