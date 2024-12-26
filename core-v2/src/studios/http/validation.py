from typing import Optional
from pydantic import BaseModel, EmailStr, Field, constr


class BatchUserInput(BaseModel):
    username: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=8, max_length=256)
    email: EmailStr


class UpdateUserInput(BaseModel):
    id: int
    username: str = Field(..., min_length=5, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=256)
    email: EmailStr
    binName:  Optional[str] = Field(None, min_length=1)
    role: int
    firstName: Optional[str] = Field(None, min_length=1)
    lastName:  Optional[str] = Field(None, min_length=1)
    displayName:  Optional[str] = Field(None, min_length=1)
    active: bool
    firebasePushnotId:  Optional[str] = Field(None)
    uploadLimit: int
    intro:  Optional[str] = Field(None, max_length=500)


class ChangePasswordInput(BaseModel):
    oldPassword: str = Field(..., min_length=8, max_length=256)
    newPassword: str = Field(..., min_length=8, max_length=256)
    id: int
