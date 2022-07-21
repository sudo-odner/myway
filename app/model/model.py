import fastapi
from pydantic import BaseModel

class SessionModel(BaseModel):
    session: str

class UserModel(BaseModel):
    name: str
    email: str

# Авторизаци и регистрация пользователя
class AuthorizationModel(BaseModel):
    login: str
    password: str

class RegistedModel(UserModel):
    login: str
    password: str

# Редактирование пользователя
class UserModel(SessionModel):
    edit: dict

class UserResultModel(UserModel):
    pass

# Завершение цели
class CompletedModel(SessionModel):
    id_task: int
