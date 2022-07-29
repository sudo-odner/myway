from typing import List
from pydantic import BaseModel, EmailStr
from requests import session

class SessionModel(BaseModel):
    session: str

class MessengTrue(BaseModel):
    message: bool

class DateModel(BaseModel):
    year: int = 1
    month: int = 1
    day: int = 1
    hours: int = 0
    minute: int = 0


# Решистрация
class RegistedModel(BaseModel):
    name: str
    email: EmailStr
    birthday: DateModel
    password: str

class RuthorizationModel(BaseModel):
    email: EmailStr
    password: str


    class Config:
        schema_extra = {
            "example": {
                "name": "First Name",
                "email": "user@example.com",
                "birthday": {
                    "year": 2005,
                    "month": 2,
                    "day": 18},
                "password": "user password"
            }
        }


# Редактирование пользователя
class UserModel(SessionModel):
    email: EmailStr = None
    birthday: DateModel = None
    name: str = None

class UserResultModel(BaseModel):
    image: str
    email: str
    birthday: str
    name: str

    class Config:
        schema_extra = {
            "example": {
                "image": "None",
                "email": "user@example.com",
                "birthday": "date",
                "name": "kirill"
            }
        }
    
class SessionAndID(BaseModel):
    session: str
    id: int