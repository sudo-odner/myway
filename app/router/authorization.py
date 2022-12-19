from fastapi import APIRouter, HTTPException
from app import DB, object_to_datetime

from app.db_setup import User
from app.model.authorization import LoginModel, RegistedModel
from pydantic import EmailStr

import hashlib

router = APIRouter()

_hash = lambda x : hashlib.md5((x).encode()).hexdigest()

########################################################### Элементы при регистрации

# Проверка регистрации пользователя
@router.get("/cheak-email")
def cheak_email(email: EmailStr):
    if DB.get_first_filter(User, search=(User.email == email)) is not None:
        raise HTTPException(status_code=406, detail="Email is registed")


########################################################### Регистрация

@router.post("/registed")
def registed(_app: RegistedModel):
    if DB.get_first_filter(User, search=(User.email == _app.email)) is not None:
        raise HTTPException(status_code=423, detail="This mail is registered")
    
    date = object_to_datetime(_app.birthday)
    user_id = DB.new_user(email=_app.email, password=_app.password, name=_app.name, birthday=date)

    return {"session": f"{DB.new_session(user_id)}"}

########################################################### Авторизация

@router.post("/login")
def login(_app: LoginModel):
    user = DB.get_first_filter(User, search=(User.email == _app.email))
    if user is None:
        raise HTTPException(status_code=423, detail="This mail is not registered") # Изменить ошибку
    
    if _hash(_app.password + user.salt) != user.hashpass:
        raise HTTPException(status_code=423, detail="Wrong password")
    
    user_session = DB.new_session(user.id)
    DB.using_app(user_session)
    
    return {"session": f"{user_session}"}