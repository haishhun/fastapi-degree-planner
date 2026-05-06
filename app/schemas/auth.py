from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    college: str | None = None
    major: str | None = None
    degree_type: str | None = None


class UserPublic(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
