from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from db import SessionLocal
from models import Users
from user_post_model import UserRequest, Token
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)

SECRET_KEY = '2b5e8d2c29b1d5113e38581b81510dfda8d2c182488e19be08ad28d93eea44c7'
ALGORITHM = 'HS256'

bcrypt_ctx = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_ctx.verify(password, user.hashed_pwd):
        return False
    return user


def create_token(username: str, id: int, role: str, expires_delta: timedelta):
    encode = {
        'sub': username,
        'id': id,
        'role': role
    }
    expires = datetime.utcnow() + expires_delta
    encode.update({
        'exp': expires
    })
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        id: int = payload.get('id')
        role: str = payload.get('role')

        if username is None or id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not validated')
        return {
            'username': username,
            'id': id,
            'role': role
        }

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not validated')


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, req: UserRequest):
    #  model = Users(**req.model_dump())
    model = Users(
        email=req.email,
        username=req.username,
        first_name=req.first_name,
        last_name=req.last_name,
        role=req.role,
        hashed_pwd=bcrypt_ctx.hash(req.password),
        is_active=True
    )

    db.add(model)
    db.commit()


@router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not validated')

    token = create_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {
        'access_token': token,
        'token_type': 'Bearer'
    }
