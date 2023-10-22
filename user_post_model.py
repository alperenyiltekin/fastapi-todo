from pydantic import BaseModel, Field


class UserRequest(BaseModel):
    username: str = Field(min_length=3)
    email: str = Field(min_length=3, max_length=250)
    first_name: str = Field(gt=0, lt=6)
    last_name: str = Field()
    password: str = Field()
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str
