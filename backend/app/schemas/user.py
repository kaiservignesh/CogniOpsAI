from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr


class UserResponse(UserCreate):
    id: int

    class Config:
        from_attributes = True