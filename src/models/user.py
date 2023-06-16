from beanie import Document, PydanticObjectId
from fastapi.security import HTTPBasicCredentials
from pydantic import BaseModel, EmailStr, Field
from bson.objectid import ObjectId


class User(Document):
    name: str = Field(max_length=50)
    email: EmailStr
    password: str = Field(max_length=200)

    class Settings:
        name = "user"

    class Config:
        schema_extra = {
            "example": {
                "name": "sherlock",
                "email": "sherlock@test.com",
                "password": "11a23DD#"
            }
        }


class UserSignIn(HTTPBasicCredentials):
    class Config:
        schema_extra = {
            "example": {
                "username": "sherlock@test.com",
                "password": "11a23DD3"
            }
        }


class UserData(BaseModel):
    name: str
    email: EmailStr

    class Config:
        schema_extra = {
            "example": {
                "name": "sherlock",
                "email": "sherlock@test.com",
            }
        }