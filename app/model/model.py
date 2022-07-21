import fastapi
from pydantic import BaseModel

class SessionModel(BaseModel):
    session: str

class UserModel(BaseModel):
    name: str
    email: str

# Авторизаци и регистрация пользователя
class AuthorizationModel(BaseModel):
    email: str
    password: str

class RegistedModel(UserModel):
    password: str

# Редактирование пользователя
class UserModel(SessionModel):
    edit: dict

# Завершение цели
class CompletedModel(SessionModel):
    id_task: int

class UserResultModel(BaseModel):
    image: str
    email: str
    name: str